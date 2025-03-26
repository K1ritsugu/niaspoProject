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
        alert("Failed to load user data. Please log in again.");
      }
    };

    fetchUserData();
  }, []);

  const updateQuantity = (id, delta) => {
    const updatedCart = cartItems
      .map((item) =>
        item.id === id ? { ...item, quantity: item.quantity + delta } : item
      )
      .filter((item) => item.quantity > 0);

    setCartItems(updatedCart);
    localStorage.setItem("cart", JSON.stringify(updatedCart));
  };

  const handleCreateOrder = async () => {
    try {
      const token = getToken();
      if (!token) {
        alert("You are not logged in. Please log in to proceed.");
        return;
      }

      const totalAmount = cartItems.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
      );

      // Создаём платеж
      const paymentResponse = await api.post(
        "/payments/pay/",
        {
          user_id: userData.id,
          amount: totalAmount,
          payment_method: paymentMethod,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Создаём заказ
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
      alert("Failed to create order. Please try again.");
    }
  };

  return (
    <div className="menu-container">
      <h2 className="text-4xl font-bold text-center my-5">Your Cart</h2>
      {cartItems.length > 0 ? (
        <>
          <ul className="cart-list">
            {cartItems.map((item) => (
              <li key={item.id} className="cart-item flex items-center justify-between">
                <img
                  src={`${process.env.REACT_APP_API_GATEWAY_URL}/menu/images/${item.image_url.split("images/")[1]}`}
                  alt={item.name}
                  className="w-16 h-16 object-cover rounded"
                />
                <div className="menu-details flex-grow px-4">
                  <h3 className="text-lg font-semibold">{item.name}</h3>
                  <p className="text-gray-500">Price: {item.price} respect</p>
                </div>
                <div className="quantity-controls flex items-center space-x-3">
                  <button
                    onClick={() => updateQuantity(item.id, -1)}
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded"
                  >
                    -
                  </button>
                  <span className="text-lg font-semibold">{item.quantity}</span>
                  <button
                    onClick={() => updateQuantity(item.id, 1)}
                    className="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-2 rounded"
                  >
                    +
                  </button>
                </div>
              </li>
            ))}
          </ul>
          <div className="order-section mt-8">
            <div className="user-address mb-4">
              <h4 className="text-lg font-semibold">Delivery Address:</h4>
              <p>{userData.address || "Loading address..."}</p>
            </div>
            <label className="block mb-4">
              Payment Method:
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="ml-2 border rounded px-2 py-1"
              >
                <option value="card">Card</option>
                <option value="cash">Cash</option>
              </select>
            </label>
            <button
              onClick={handleCreateOrder}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Place Order
            </button>
          </div>
        </>
      ) : (
        <p className="text-center text-lg text-gray-500">Your cart is empty.</p>
      )}
    </div>
  );
}

export default Cart;
