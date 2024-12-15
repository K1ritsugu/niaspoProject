import React, { useEffect, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

function MenuList() {
  const [menu, setMenu] = useState([]); // Текущие блюда
  const [cart, setCart] = useState(
    JSON.parse(localStorage.getItem("cart")) || []
  );
  const [currentPage, setCurrentPage] = useState(1); // Текущая страница
  const [totalItems, setTotalItems] = useState(0); // Общее количество блюд
  const itemsPerPage = 12; // Количество блюд на странице

  // Получение блюд с пагинацией
  useEffect(() => {
    const fetchMenu = async () => {
      try {
        const skip = (currentPage - 1) * itemsPerPage;
        const response = await axios.get(
          `${process.env.REACT_APP_API_GATEWAY_URL}/menu/dishes?skip=${skip}&limit=${itemsPerPage}`
        );
        setMenu(response.data.dishes || response.data); // Обновление меню
        setTotalItems(response.data.total || 0); // Общее количество (если приходит)
      } catch (error) {
        console.error("Error fetching menu", error);
      }
    };
    fetchMenu();
  }, [currentPage]);

  // Добавление в корзину
  const addToCart = (item) => {
    setCart((prevCart) => {
      const updatedCart = prevCart.some((cartItem) => cartItem.id === item.id)
        ? prevCart.map((cartItem) =>
            cartItem.id === item.id
              ? { ...cartItem, quantity: cartItem.quantity + 1 }
              : cartItem
          )
        : [...prevCart, { ...item, quantity: 1 }];

      localStorage.setItem("cart", JSON.stringify(updatedCart)); // Обновление localStorage
      return updatedCart;
    });
  };

  // Обновление количества
  const updateQuantity = (id, delta) => {
    setCart((prevCart) => {
      const updatedCart = prevCart
        .map((item) =>
          item.id === id ? { ...item, quantity: item.quantity + delta } : item
        )
        .filter((item) => item.quantity > 0); // Удаляем, если количество <= 0
      localStorage.setItem("cart", JSON.stringify(updatedCart));
      return updatedCart;
    });
  };

  // Пагинация
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <div className="container mx-auto px-5 py-10">
      <h2 className="text-4xl font-bold text-center mb-10">Menu</h2>

      {/* Сетка с блюдами */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
        {menu.map((item) => {
          const cartItem = cart.find((cartItem) => cartItem.id === item.id);
          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-lg shadow-lg overflow-hidden"
            >
              <img
                src={`${process.env.REACT_APP_API_GATEWAY_URL}/menu/images/${item.image_url.split("images/")[1]}`}
                alt={item.name}
                className="w-full h-48 object-cover cursor-pointer"
              />
              <div className="p-4 text-center">
                <h3 className="text-lg font-semibold">{item.name}</h3>
                <p className="text-gray-500">{item.description}</p>
                <p className="text-lg font-bold mt-2">${item.price}</p>

                {/* Управление количеством */}
                {cartItem ? (
                  <div className="flex justify-center items-center mt-3">
                    <button
                      onClick={() => updateQuantity(item.id, -1)}
                      className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                    >
                      -
                    </button>
                    <span className="mx-3 text-lg font-bold">
                      {cartItem.quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(item.id, 1)}
                      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    >
                      +
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => addToCart(item)}
                    className="mt-3 bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                  >
                    Add to Cart
                  </button>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Пагинация */}
      <div className="flex justify-center items-center mt-8">
        <button
          onClick={() => goToPage(currentPage - 1)}
          disabled={currentPage === 1}
          className={`mx-2 px-4 py-2 font-bold rounded ${
            currentPage === 1
              ? "bg-gray-300 text-gray-500 cursor-not-allowed"
              : "bg-gray-200 hover:bg-gray-300 text-gray-700"
          }`}
        >
          Previous
        </button>
        <span className="mx-4 text-lg">
          Page {currentPage} of {totalPages || 1}
        </span>
        <button
          onClick={() => goToPage(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className={`mx-2 px-4 py-2 font-bold rounded ${
            currentPage >= totalPages
              ? "bg-gray-300 text-gray-500 cursor-not-allowed"
              : "bg-gray-200 hover:bg-gray-300 text-gray-700"
          }`}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default MenuList;
