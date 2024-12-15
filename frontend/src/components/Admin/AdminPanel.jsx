import React, { useState, useEffect } from "react";
import api from "../../utils/api";
import { getToken, getUserRole } from "../../utils/auth";
import "../../styles/Admin.css";
import { useNavigate } from "react-router-dom";

function AdminPanel() {
  const [dishes, setDishes] = useState([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [image, setImage] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const checkRoleAndFetchDishes = async () => {
      const role = await getUserRole();
      if (role !== "admin") {
        alert("Access Denied");
        navigate("/menu");
        return;
      }

      const response = await api.get("/menu/dishes/?limit=100");
      setDishes(response.data.dishes);
    };

    checkRoleAndFetchDishes();
  }, [navigate]);

  const handleImageUpload = (e) => setImage(e.target.files[0]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("name", name);
    formData.append("description", description);
    formData.append("price", price);
    formData.append("image", image);

    try {
      await api.post("/menu/dishes/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${getToken()}`,
        },
      });
      alert("Dish created successfully!");
      window.location.reload();
    } catch (error) {
      console.error("Failed to add dish:", error);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this dish?")) {
      try {
        await api.delete(`/menu/dishes/${id}`, {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          },
        });
        setDishes((prevDishes) => prevDishes.filter((dish) => dish.id !== id));
        alert("Dish deleted successfully!");
      } catch (error) {
        console.error("Failed to delete dish:", error);
        alert("Failed to delete dish.");
      }
    }
  };

  return (
    <div className="admin-container">
      <h2>Admin Panel</h2>
      <form onSubmit={handleSubmit} encType="multipart/form-data">
        <input
          type="text"
          placeholder="Dish Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
        <input
          type="number"
          placeholder="Price"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          required
        />
        <input type="file" accept="image/*" onChange={handleImageUpload} required />
        <button type="submit">Add Dish</button>
      </form>

      <h3>Existing Dishes</h3>
      <ul className="menu-container grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {dishes.map((dish) => (
          <li key={dish.id} className="relative bg-white shadow-lg rounded-lg overflow-hidden">
            <button
              onClick={() => handleDelete(dish.id)}
              className="absolute down-10 bg-red-500 text-white w-8 h-8 flex items-center justify-center rounded-full hover:bg-red-700"
              title="Delete Dish"
            >
              &times;
            </button>
            <img
              src={`${process.env.REACT_APP_API_GATEWAY_URL}/menu/images/${dish.image_url.split("images/")[1]}`}
              alt={dish.name}
              className="w-full h-40 object-cover"
            />
            <div className="p-4 text-center">
              <h3 className="text-lg font-bold">{dish.name}</h3>
              <p className="text-gray-500">{dish.description}</p>
              <p className="text-green-600 font-bold mt-2">${dish.price}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AdminPanel;
