import html

def test_parse(text):
    parts = text.split()
    if len(parts) < 4:
        print("Help needed")
        return
    try:
        sell = float(parts[-1])
        cost = float(parts[-2])
        product_id = " ".join(parts[1:-2])
        print(f"Parsed product_id='{product_id}', cost={cost}, sell={sell}")
    except Exception as e:
        print(f"Error: {e}")

test_parse("/narx Pechini 1 38000 46000")
