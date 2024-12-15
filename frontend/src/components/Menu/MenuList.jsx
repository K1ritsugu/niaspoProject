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
  const [selectedItem, setSelectedItem] = useState(null); // Выбранный элемент для попапа
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
      const updatedCart = prevCart.find((cartItem) => cartItem.id === item.id)
        ? prevCart.map((cartItem) =>
            cartItem.id === item.id
              ? { ...cartItem, quantity: cartItem.quantity + 1 }
              : cartItem
          )
        : [...prevCart, { ...item, quantity: 1 }];
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
                onClick={() => setSelectedItem(item)} // Открытие модального окна
              />
              <div className="p-4 text-center">
                <h3 className="text-lg font-semibold">{item.name}</h3>
                <p className="text-gray-500">{item.description}</p>
                <p className="text-lg font-bold mt-2">${item.price}</p>
                <button
                  onClick={() => addToCart(item)}
                  className="mt-3 bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                >
                  Add to Cart
                </button>
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

      {/* Модальное окно */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-4xl p-6 relative">
            <button
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
              onClick={() => setSelectedItem(null)}
            >
              ✖
            </button>
            <div className="flex flex-col md:flex-row items-center">
              <img
                src={`${process.env.REACT_APP_API_GATEWAY_URL}/menu/images/${selectedItem.image_url.split("images/")[1]}`}
                alt={selectedItem.name}
                className="w-full md:w-1/2 h-auto object-contain"
              />
              <div className="md:ml-6 mt-4 md:mt-0 text-center md:text-left">
                <h3 className="text-2xl font-bold mb-2">{selectedItem.name}</h3>
                <p className="text-gray-500 mb-4">{selectedItem.description}</p>
                <p className="text-lg font-bold mb-4">${selectedItem.price}</p>
                <button
                  onClick={() => {
                    addToCart(selectedItem);
                    setSelectedItem(null);
                  }}
                  className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded w-full md:w-auto"
                >
                  Add to Cart
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MenuList;
