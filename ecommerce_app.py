from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from mini_rdbms import Database, Column
from fastapi.staticfiles import StaticFiles
from typing import Optional


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

db = Database()

db.create_table("products", [
    Column("id", "integer", primary=True),
    Column("name", "string"),
    Column("price", "float"),
])

db.create_table("orders", [
    Column("id", "integer", primary=True),
    Column("product_id", "integer"),
    Column("quantity", "integer"),
    Column("total_price", "float"),
])

db.tables["products"].insert({"id": 1, "name": "Laptop", "price": 800})
db.tables["products"].insert({"id": 2, "name": "Phone", "price": 500})


@app.post("/orders")
def create_order(product_id: int, quantity: int):
    product = db.tables["products"].select({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    total = product[0]["price"] * quantity
    # Generate a unique ID (simple increment for now)
    new_id = 1
    if db.tables["orders"].rows:
        new_id = max(r["id"] for r in db.tables["orders"].rows) + 1
        
    db.tables["orders"].insert({
        "id": new_id,
        "product_id": product_id, 
        "quantity": quantity, 
        "total_price": total
    })
    return {"message": "Order created successfully"}


@app.get("/orders")
def get_orders():
    # Return joined results so we can see product names
    return db.tables["orders"].join(db.tables["products"], "product_id", "id")


@app.put("/orders/{order_id}")
def update_order(order_id: int, quantity: int):
    order = db.tables["orders"].select({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    product_id = order[0]["product_id"]
    product = db.tables["products"].select({"id": product_id})
    total = product[0]["price"] * quantity
    
    db.tables["orders"].update(
        {"quantity": quantity, "total_price": total},
        {"id": order_id}
    )
    return {"message": "Order updated successfully"}


@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    db.tables["orders"].delete({"id": order_id})
    return {"message": "Order deleted successfully"}


@app.get("/", response_class=HTMLResponse)
def home():
    products = db.tables["products"].select()
    product_options = "".join([f'<option value="{p["id"]}">{p["name"]} - ${p["price"]}</option>' for p in products])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nai Store | Next-Gen E-commerce</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="./static/style.css">
        <style>
            .action-btn {{
                padding: 0.5rem;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.8rem;
                border: none;
                transition: opacity 0.2s;
            }}
            .edit-btn {{ background: var(--primary); color: white; }}
            .delete-btn {{ background: #ef4444; color: white; margin-left: 0.5rem; }}
            .action-btn:hover {{ opacity: 0.8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Nai Store</h1>
                <p style="color: var(--text-muted)">The future of digital commerce is here.</p>
            </header>

            <div class="grid">
                <!-- Product List Card -->
                <div class="card">
                    <h2>📦 Available Products</h2>
                    <ul class="product-list">
                        {" ".join([f'<li class="product-item"><span>{p["name"]}</span><span class="tag">${p["price"]}</span></li>' for p in products])}
                    </ul>
                </div>

                <!-- Create Order Card -->
                <div class="card">
                    <h2>🛒 Create New Order</h2>
                    <form id="orderForm">
                        <div class="form-group">
                            <label>Select Product</label>
                            <select name="product_id" required>
                                {product_options}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Quantity</label>
                            <input type="number" name="quantity" min="1" value="1" required>
                        </div>
                        <button type="submit">Place Order</button>
                    </form>
                </div>
            </div>

            <div id="orders-container" class="card">
                <h2>📈 Recent Orders</h2>
                <div style="overflow-x: auto;">
                    <table class="order-table">
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Total Price</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="ordersBody">
                            <!-- Populated via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="toast" class="toast">Action Successful!</div>

        <script>
            async function loadOrders() {{
                const response = await fetch('/orders');
                const orders = await response.json();
                const tbody = document.getElementById('ordersBody');
                tbody.innerHTML = orders.map(o => `
                    <tr>
                        <td>#${{o.orders_id}}</td>
                        <td>${{o.products_name}}</td>
                        <td>${{o.orders_quantity}}</td>
                        <td><span style="color: var(--accent); font-weight: 600;">$${{o.orders_total_price.toFixed(2)}}</span></td>
                        <td>
                            <button onclick="editOrder(${{o.orders_id}}, ${{o.orders_quantity}})" class="action-btn edit-btn">Edit</button>
                            <button onclick="deleteOrder(${{o.orders_id}})" class="action-btn delete-btn">Delete</button>
                        </td>
                    </tr>
                `).join('') || '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No orders yet</td></tr>';
            }}

            document.getElementById('orderForm').onsubmit = async (e) => {{
                e.preventDefault();
                const formData = new FormData(e.target);
                const productId = formData.get('product_id');
                const quantity = formData.get('quantity');

                try {{
                    const response = await fetch(`/orders?product_id=${{productId}}&quantity=${{quantity}}`, {{
                        method: 'POST'
                    }});
                    
                    if (response.ok) {{
                        showToast("Order Placed Successfully!");
                        loadOrders();
                        e.target.reset();
                    }}
                }} catch (err) {{
                    console.error(err);
                }}
            }};

            async function editOrder(id, currentQty) {{
                const newQty = prompt("Enter new quantity:", currentQty);
                if (newQty !== null && newQty !== "" && !isNaN(newQty)) {{
                    try {{
                        const response = await fetch(`/orders/${{id}}?quantity=${{newQty}}`, {{
                            method: 'PUT'
                        }});
                        if (response.ok) {{
                            showToast("Order Updated!");
                            loadOrders();
                        }}
                    }} catch (err) {{
                        console.error(err);
                    }}
                }}
            }}

            async function deleteOrder(id) {{
                if (confirm("Are you sure you want to delete this order?")) {{
                    try {{
                        const response = await fetch(`/orders/${{id}}`, {{
                            method: 'DELETE'
                        }});
                        if (response.ok) {{
                            showToast("Order Deleted!");
                            loadOrders();
                        }}
                    }} catch (err) {{
                        console.error(err);
                    }}
                }}
            }}

            function showToast(message) {{
                const toast = document.getElementById('toast');
                toast.textContent = message;
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 3000);
            }}

            loadOrders();
            setInterval(loadOrders, 10000);
        </script>
    </body>
    </html>
    """
    return html_content
