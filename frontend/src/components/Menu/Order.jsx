import React, { useEffect, useState } from "react";
import api from "../../utils/api";
import { getToken } from "../../utils/auth";
import "../../styles/Menu.css";

function Order() {
  const [orders, setOrders] = useState([]);
  const [userAddress, setUserAddress] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchOrdersWithDetails = async () => {
      try {
        const token = getToken();
        if (!token) {
          setError("No authentication token. Please log in.");
          return;
        }

        // Получаем адрес пользователя из профиля
        const userResponse = await api.get("/users/users/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUserAddress(userResponse.data.address);

        // Запрос на получение всех заказов
        const ordersResponse = await api.get("/payments/orders/", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const ordersData = ordersResponse.data;

        // Подгружаем детали каждого блюда
        const ordersWithDetails = await Promise.all(
          ordersData.map(async (order) => {
            const detailedItems = await Promise.all(
              order.items.map(async (item) => {
                const dishResponse = await api.get(`/menu/dishes/${item.dish_id}`, {
                  headers: { Authorization: `Bearer ${token}` },
                });
                return {
                  ...item,
                  name: dishResponse.data.name,
                  price: dishResponse.data.price,
                  image_url: dishResponse.data.image_url,
                };
              })
            );
            return { ...order, items: detailedItems };
          })
        );

        setOrders(ordersWithDetails);
      } catch (err) {
        console.error("Error fetching orders:", err);
        setError("Failed to fetch orders. Please try again later.");
      }
    };

    fetchOrdersWithDetails();
  }, []);

  return (
    <div className="order-container">
      <h2>Your Orders</h2>
      {error && <p className="error">{error}</p>}
      {orders.length > 0 ? (
        <ul>
          {orders.map((order) => (
            <li key={order.id} className="order-item">
              <p><strong>Order ID:</strong> {order.id}</p>
              <p><strong>Transaction ID:</strong> {order.transaction_id}</p>
              <p><strong>Status:</strong> {order.status}</p>
              <p><strong>Created At:</strong> {new Date(order.created_at).toLocaleString()}</p>
              <p><strong>Delivery Address:</strong> {userAddress}</p>
              <h4>Items:</h4>
              <ul>
                {order.items.map((item, index) => (
                  <li key={index} className="order-dish">
                    <img
                      src={`${process.env.REACT_APP_API_GATEWAY_URL}/menu/images/${item.image_url.split("images/")[1]}`}
                      alt={item.name}
                      className="menu-image"
                    />
                    <div>
                      <h3>{item.name}</h3>
                      <p>Amount: {item.amount}</p>
                      <p>Price: ${item.price}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      ) : (
        <p>You have no orders yet.</p>
      )}
    </div>
  );
}

export default Order;
