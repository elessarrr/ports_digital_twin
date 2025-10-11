from pptx import Presentation

prs = Presentation()
for i, layout in enumerate(prs.slide_layouts):
    print(f"Layout {i}: {layout.name}")
    for shape in layout.placeholders:
        print(f"  - Placeholder: {shape.placeholder_format.idx}, {shape.name}, {shape.placeholder_format.type}")