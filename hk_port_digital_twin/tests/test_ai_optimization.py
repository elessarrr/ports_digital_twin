import pytest
from datetime import datetime, timedelta
import pandas as pd
from unittest.mock import MagicMock

from hk_port_digital_twin.ai import BerthAllocationOptimizer, Ship, Berth
from hk_port_digital_twin.ai.optimization import OptimizationResult
from hk_port_digital_twin.ai.predictive_models import ShipArrivalPredictor, ArrivalPrediction
from hk_port_digital_twin.ai.decision_support import DecisionSupportEngine, Recommendation, DecisionContext, RecommendationType

@pytest.fixture
def sample_ships():
    return [
        Ship(id="SHIP001", arrival_time=datetime.now(), ship_type="container", size=2000, priority=2, containers_to_load=150, containers_to_unload=100),
        Ship(id="SHIP002", arrival_time=datetime.now() + timedelta(hours=1), ship_type="bulk", size=5000, priority=1),
        Ship(id="SHIP003", arrival_time=datetime.now() + timedelta(hours=2), ship_type="container", size=1500, priority=3, containers_to_load=200, containers_to_unload=50),
    ]

@pytest.fixture
def sample_berths():
    return [
        Berth(id="BERTH_A", capacity=6000, crane_count=3, suitable_ship_types=["container", "general"]),
        Berth(id="BERTH_B", capacity=8000, crane_count=2, suitable_ship_types=["bulk", "tanker"]),
        Berth(id="BERTH_C", capacity=4000, crane_count=4, suitable_ship_types=["container"]),
    ]

class TestOptimization:
    def test_berth_allocation(self, sample_ships, sample_berths):
        optimizer = BerthAllocationOptimizer()
        for ship in sample_ships:
            optimizer.add_ship(ship)
        for berth in sample_berths:
            optimizer.add_berth(berth)
        
        result = optimizer.optimize_berth_allocation()
        
        assert isinstance(result, OptimizationResult)
        assert len(result.ship_berth_assignments) > 0
        assert result.total_waiting_time >= 0
        assert "BERTH_A" in result.berth_utilization

class TestPredictiveModels:
    @pytest.fixture
    def mock_historical_data(self):
        return pd.DataFrame({
            'arrival_time': pd.to_datetime(['2023-01-01 10:00', '2023-01-01 12:00', '2023-01-02 14:00']),
            'ship_id': ['SHIP001', 'SHIP002', 'SHIP003'],
            'ship_type': ['container', 'bulk', 'container'],
            'size': [2000, 5000, 1500]
        })

    def test_ship_arrival_predictor_initialization(self):
        predictor = ShipArrivalPredictor()
        assert predictor is not None
        assert not predictor.is_trained

    def test_ship_arrival_predictor_train_and_predict(self, mock_historical_data):
        predictor = ShipArrivalPredictor()
        predictor.load_historical_data(mock_historical_data)
        predictor.train_arrival_model()
        assert predictor.is_trained

        prediction = predictor.predict_next_arrival(ship_type='container')
        
        assert isinstance(prediction, ArrivalPrediction)
        assert isinstance(prediction.predicted_time, datetime)
        assert isinstance(prediction.probability, float)

class TestDecisionSupport:
    def test_decision_support_engine(self, sample_ships, sample_berths):
        # Create a scenario with a long queue to trigger a recommendation
        long_queue_ships = sample_ships + [
            Ship(id=f"SHIP{i:03d}", arrival_time=datetime.now() + timedelta(hours=i), ship_type="container", size=2000, priority=2, containers_to_load=100, containers_to_unload=50)
            for i in range(4, 7)
        ]

        context = DecisionContext(
            current_time=datetime.now(),
            active_ships=[vars(s) for s in long_queue_ships],
            available_berths=[vars(b) for b in sample_berths],
            port_status={},
            resource_utilization={'berths': 0.9},
            weather_conditions={},
            operational_constraints=[],
            performance_metrics={}
        )
        
        engine = DecisionSupportEngine()
        recommendations = engine.analyze_situation(context)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        berth_recommendation_found = False
        for rec in recommendations:
            assert isinstance(rec, Recommendation)
            if rec.type == RecommendationType.BERTH_ALLOCATION:
                berth_recommendation_found = True
                assert "queue" in rec.title.lower()
        
        assert berth_recommendation_found, "Berth allocation recommendation not found"