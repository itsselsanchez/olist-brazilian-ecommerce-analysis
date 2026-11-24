from IPython.display import display, HTML
from src.utils.table_template import display_stylized_table


def display_dataset_at_a_glance(
    n_observations: str,
    n_features: int,
    purchase_window: str,
) -> None:
    """
    Display a styled summary table for the order_details dataset.
    """
    rows = [
        ("Rows", n_observations),
        ("Features", n_features),
        ("Granularity", "Order-item level"),
        ("Order purchase window", purchase_window),
        ("Source", "<code>order_details.parquet</code> (output of <em>Data Preparation and Merging</em>)"),
        ("Marketplace entities", "Customers, sellers, products, orders, order items, payments, reviews, geolocation data, and product category translations"),
        ("Representative engineered features", 
        "Logistics (<code>delivery_delay_days</code>, ""<code>customer_seller_distance_miles</code>)<br><br>"
        "Pricing (<code>freight_to_price_ratio</code>)<br><br>"
        "Seller profiling (<code>seller_type</code>, ""category concentration metrics)<br><br>"
        "Product characteristics (<code>product_volume_cm3</code>)"),
        ("Note", "Outliers were retained. Missing delivery timestamps primarily correspond to valid order lifecycle states, including canceled, unavailable, and in-transit orders."),
    ]

    display_stylized_table(
        title="All Orders Dataset at a Glance",
        headers=("Attribute", "Details"),
        rows=[(f"<b>{label}</b>", value) for label, value in rows],
    )