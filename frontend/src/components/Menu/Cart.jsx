import React, { useState, useEffect } from "react";
import api from "../../utils/api";
import { getToken } from "../../utils/auth";
import "../../styles/Menu.css";

function Cart() {
  const [cartItems, setCartItems] = useState(
    JSON.parse(localStorage.getItem("cart")) || []
  );
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [userData, setUserData] = useState({ address: "", id: null });

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = getToken();
        const response = await api.get("/users/users/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUserData({ address: response.data.address, id: response.data.id });
      } catch (error) {
        console.error("Failed to fetch user data:", error);
      }
    };

    fetchUserData();
  }, []);

  const updateQuantity = (id, delta) => {
    setCartItems((prevCart) => {
      const updatedCart = prevCart
        .map((item) =>
          item.id === id ? { ...item, quantity: item.quantity + delta } : item
        )
        .filter((item) => item.quantity > 0); // Удаляем, если 0
      localStorage.setItem("cart", JSON.stringify(updatedCart));
      return updatedCart;
    });
  };

  const handleCreateOrder = async () => {
    try {
      const token = getToken();
      const totalAmount = cartItems.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
      );

      const paymentResponse = await api.post(
        "/payments/pay/",
        {
          user_id: userData.id,
          amount: totalAmount,
          payment_method: paymentMethod,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      await api.post(
        "/payments/orders/",
        {
          user_id: userData.id,
          transaction_id: paymentResponse.data.id,
          payment_method: paymentMethod,
          items: cartItems.map((item) => ({
            dish_id: item.id,
            amount: item.quantity,
          })),
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      alert("Order created successfully!");
      localStorage.removeItem("cart");
      setCartItems([]);
    } catch (error) {
      console.error("Failed to create order:", error);
    }
  };

  return (
    <div className="menu-container">
      <h2>Ваша корзина</h2>
      {cartItems.length > 0 ? (
        <>
          <ul>
            {cartItems.map((item) => (
              <li key={item.id} className="cart-item">
                <img
                  src={`${process.env.REACT_APP_API_GATEWAY_URL}/menu/images/${item.image_url.split("images/")[1]}`}
                  alt={item.name}
                  className="menu-image"
                />
                <div className="menu-details">
                  <h3>{item.name}</h3>
                  <p>Price: ${item.price}</p>
                </div>
                <div className="quantity-controls">
                  <button onClick={() => updateQuantity(item.id, -1)}>-</button>
                  <span>{item.quantity}</span>
                  <button onClick={() => updateQuantity(item.id, 1)}>+</button>
                </div>
              </li>
            ))}
          </ul>
          <div className="order-section">
            <div className="user-address">
              <h4>Адрес доставки:</h4>
              <p>{userData.address || "Загрузка адреса..."}</p>
            </div>
            <label>
              Payment Method:
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                <option value="card">Card</option>
                <option value="cash">Cash</option>
              </select>
            </label>
            <button onClick={handleCreateOrder} className="create-order-btn">
              Создать заказ
            </button>
          </div>
        </>
      ) : (
        <p>Ваша корзина пуста.</p>
      )}
    </div>
  );
}

export default Cart;
