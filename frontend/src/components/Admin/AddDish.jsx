import React, { useState } from "react";
import api from "../../utils/api";
import "../../styles/Admin.css";

function AddDish() {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/menu", { name, price });
      alert("Dish added successfully!");
      setName("");
      setPrice("");
    } catch (error) {
      alert("Failed to add dish!");
    }
  };

  return (
    <div className="admin-container">
      <form onSubmit={handleSubmit}>
        <h2>Add Dish</h2>
        <input
          type="text"
          placeholder="Dish Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="number"
          placeholder="Price"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          required
        />
        <button type="submit">Add Dish</button>
      </form>
    </div>
  );
}

export default AddDish;