"""
Progressive Data Loader for Large Datasets

This module provides utilities for loading large datasets progressively,
implementing chunking, lazy loading, and memory-efficient data processing
for the Streamlit dashboard.
"""

import pandas as pd
import numpy as np
from typing import Iterator, Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass
from enum import Enum
import streamlit as st
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
import time

# Configure logging
logger = logging.getLogger(__name__)

class LoadingStrategy(Enum):
    """Data loading strategies for different use cases."""
    CHUNK = "chunk"          # Load data in chunks
    LAZY = "lazy"            # Load data on-demand
    PROGRESSIVE = "progressive"  # Load data progressively with UI updates
    PARALLEL = "parallel"    # Load data using parallel processing

@dataclass
class LoadingConfig:
    """Configuration for progressive data loading."""
    chunk_size: int = 1000
    strategy: LoadingStrategy = LoadingStrategy.PROGRESSIVE
    show_progress: bool = True
    cache_chunks: bool = True
    max_workers: int = 4
    memory_limit_mb: int = 500

class ProgressiveDataLoader:
    """
    Progressive data loader for handling large datasets efficiently.
    """
    
    def __init__(self, config: Optional[LoadingConfig] = None):
        """
        Initialize the progressive data loader.
        
        Args:
            config: Loading configuration
        """
        self.config = config or LoadingConfig()
        self._chunk_cache = {}
        self._total_rows = 0
        self._loaded_rows = 0
        
    def load_csv_progressive(
        self, 
        file_path: Union[str, Path], 
        progress_container: Optional[st.container] = None,
        **pandas_kwargs
    ) -> Iterator[pd.DataFrame]:
        """
        Load CSV file progressively in chunks.
        
        Args:
            file_path: Path to the CSV file
            progress_container: Streamlit container for progress display
            **pandas_kwargs: Additional arguments for pandas.read_csv
            
        Yields:
            DataFrame chunks
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Estimate total rows for progress tracking
        if self.config.show_progress and progress_container:
            self._total_rows = self._estimate_total_rows(file_path)
            progress_bar = progress_container.progress(0)
            status_text = progress_container.empty()
        
        try:
            # Read CSV in chunks
            chunk_reader = pd.read_csv(
                file_path,
                chunksize=self.config.chunk_size,
                **pandas_kwargs
            )
            
            chunk_num = 0
            for chunk in chunk_reader:
                chunk_num += 1
                self._loaded_rows += len(chunk)
                
                # Update progress
                if self.config.show_progress and progress_container:
                    progress = min(self._loaded_rows / self._total_rows, 1.0) if self._total_rows > 0 else 0
                    progress_bar.progress(progress)
                    status_text.text(f"Loading chunk {chunk_num}: {self._loaded_rows:,} rows loaded")
                
                # Cache chunk if enabled
                if self.config.cache_chunks:
                    self._chunk_cache[chunk_num] = chunk
                
                yield chunk
                
                # Memory management
                if self._check_memory_usage():
                    logger.warning("Memory limit reached, clearing cache")
                    self._clear_cache()
        
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            if self.config.show_progress and progress_container:
                status_text.error(f"Error loading data: {e}")
            raise
        
        finally:
            if self.config.show_progress and progress_container:
                status_text.success(f"Loading complete: {self._loaded_rows:,} rows loaded")
    
    def load_dataframe_lazy(
        self, 
        df: pd.DataFrame, 
        filter_func: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None
    ) -> Iterator[pd.DataFrame]:
        """
        Load DataFrame lazily in chunks with optional filtering.
        
        Args:
            df: Source DataFrame
            filter_func: Optional function to filter each chunk
            
        Yields:
            Filtered DataFrame chunks
        """
        total_chunks = len(df) // self.config.chunk_size + (1 if len(df) % self.config.chunk_size else 0)
        
        for i in range(0, len(df), self.config.chunk_size):
            chunk = df.iloc[i:i + self.config.chunk_size].copy()
            
            # Apply filter if provided
            if filter_func:
                chunk = filter_func(chunk)
            
            if not chunk.empty:
                yield chunk
    
    def load_parallel(
        self, 
        file_paths: List[Union[str, Path]], 
        progress_container: Optional[st.container] = None
    ) -> List[pd.DataFrame]:
        """
        Load multiple files in parallel.
        
        Args:
            file_paths: List of file paths to load
            progress_container: Streamlit container for progress display
            
        Returns:
            List of loaded DataFrames
        """
        if self.config.show_progress and progress_container:
            progress_bar = progress_container.progress(0)
            status_text = progress_container.empty()
        
        def load_single_file(file_path):
            """Load a single file."""
            try:
                return pd.read_csv(file_path)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                return pd.DataFrame()
        
        results = []
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = [executor.submit(load_single_file, fp) for fp in file_paths]
            
            for i, future in enumerate(futures):
                result = future.result()
                results.append(result)
                
                # Update progress
                if self.config.show_progress and progress_container:
                    progress = (i + 1) / len(file_paths)
                    progress_bar.progress(progress)
                    status_text.text(f"Loaded {i + 1}/{len(file_paths)} files")
        
        if self.config.show_progress and progress_container:
            status_text.success(f"All {len(file_paths)} files loaded successfully")
        
        return results
    
    def _estimate_total_rows(self, file_path: Path) -> int:
        """
        Estimate total number of rows in CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Estimated number of rows
        """
        try:
            # Quick estimation by reading first chunk and file size
            sample_chunk = pd.read_csv(file_path, nrows=1000)
            file_size = file_path.stat().st_size
            
            # Estimate based on sample
            sample_size = len(str(sample_chunk.to_csv()))
            estimated_rows = int((file_size / sample_size) * len(sample_chunk))
            
            return max(estimated_rows, 1000)  # Minimum estimate
        except Exception:
            return 10000  # Default fallback
    
    def _check_memory_usage(self) -> bool:
        """
        Check if memory usage exceeds limit.
        
        Returns:
            True if memory limit exceeded
        """
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return memory_mb > self.config.memory_limit_mb
        except ImportError:
            # If psutil not available, use cache size as proxy
            return len(self._chunk_cache) > 50
    
    def _clear_cache(self):
        """Clear the chunk cache to free memory."""
        self._chunk_cache.clear()
    
    def get_cached_chunk(self, chunk_num: int) -> Optional[pd.DataFrame]:
        """
        Get a cached chunk by number.
        
        Args:
            chunk_num: Chunk number
            
        Returns:
            Cached DataFrame or None
        """
        return self._chunk_cache.get(chunk_num)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_chunks': len(self._chunk_cache),
            'total_rows_loaded': self._loaded_rows,
            'memory_usage_mb': len(str(self._chunk_cache)) / 1024 / 1024
        }

class StreamlitDataLoader:
    """
    Streamlit-specific data loader with UI components.
    """
    
    @staticmethod
    def create_loading_interface(
        container: st.container,
        title: str = "Loading Data"
    ) -> Dict[str, Any]:
        """
        Create a loading interface in Streamlit.
        
        Args:
            container: Streamlit container
            title: Loading title
            
        Returns:
            Dictionary with UI components
        """
        with container:
            st.subheader(title)
            progress_bar = st.progress(0)
            status_text = st.empty()
            details_expander = st.expander("Loading Details", expanded=False)
            
            return {
                'progress_bar': progress_bar,
                'status_text': status_text,
                'details_expander': details_expander,
                'container': container
            }
    
    @staticmethod
    def load_with_ui(
        loader: ProgressiveDataLoader,
        file_path: Union[str, Path],
        container: st.container,
        process_func: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None
    ) -> pd.DataFrame:
        """
        Load data with UI feedback.
        
        Args:
            loader: ProgressiveDataLoader instance
            file_path: Path to data file
            container: Streamlit container for UI
            process_func: Optional function to process each chunk
            
        Returns:
            Combined DataFrame
        """
        ui_components = StreamlitDataLoader.create_loading_interface(
            container, f"Loading {Path(file_path).name}"
        )
        
        chunks = []
        start_time = time.time()
        
        try:
            for chunk in loader.load_csv_progressive(file_path, container):
                if process_func:
                    chunk = process_func(chunk)
                chunks.append(chunk)
                
                # Update details
                with ui_components['details_expander']:
                    st.write(f"Chunks loaded: {len(chunks)}")
                    st.write(f"Rows processed: {sum(len(c) for c in chunks):,}")
                    st.write(f"Time elapsed: {time.time() - start_time:.1f}s")
            
            # Combine all chunks
            if chunks:
                result_df = pd.concat(chunks, ignore_index=True)
                ui_components['status_text'].success(
                    f"✅ Loaded {len(result_df):,} rows in {time.time() - start_time:.1f}s"
                )
                return result_df
            else:
                ui_components['status_text'].warning("No data loaded")
                return pd.DataFrame()
                
        except Exception as e:
            ui_components['status_text'].error(f"❌ Error loading data: {e}")
            raise

# Convenience functions
def create_progressive_loader(
    chunk_size: int = 1000,
    strategy: LoadingStrategy = LoadingStrategy.PROGRESSIVE,
    show_progress: bool = True
) -> ProgressiveDataLoader:
    """
    Create a progressive data loader with specified configuration.
    
    Args:
        chunk_size: Size of each data chunk
        strategy: Loading strategy to use
        show_progress: Whether to show progress indicators
        
    Returns:
        Configured ProgressiveDataLoader
    """
    config = LoadingConfig(
        chunk_size=chunk_size,
        strategy=strategy,
        show_progress=show_progress
    )
    return ProgressiveDataLoader(config)

def load_large_csv(
    file_path: Union[str, Path],
    container: Optional[st.container] = None,
    chunk_size: int = 1000,
    **pandas_kwargs
) -> pd.DataFrame:
    """
    Convenience function to load large CSV files progressively.
    
    Args:
        file_path: Path to CSV file
        container: Optional Streamlit container for progress display
        chunk_size: Size of each chunk
        **pandas_kwargs: Additional pandas arguments
        
    Returns:
        Loaded DataFrame
    """
    loader = create_progressive_loader(chunk_size=chunk_size)
    
    if container:
        return StreamlitDataLoader.load_with_ui(loader, file_path, container)
    else:
        chunks = list(loader.load_csv_progressive(file_path, **pandas_kwargs))
        return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()