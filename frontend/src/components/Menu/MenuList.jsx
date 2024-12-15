import React, { useEffect, useState } from "react";
import axios from "axios";

function MenuList() {
  const [menu, setMenu] = useState([]);
  const [cart, setCart] = useState(JSON.parse(localStorage.getItem("cart")) || []);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 12;

  // Состояния для модального окна
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedDish, setSelectedDish] = useState(null);

  useEffect(() => {
    const fetchMenu = async () => {
      try {
        const skip = (currentPage - 1) * itemsPerPage;
        const response = await axios.get(
          `${process.env.REACT_APP_API_GATEWAY_URL}/menu/dishes?skip=${skip}&limit=${itemsPerPage}`
        );
        setMenu(response.data.dishes || response.data);
        setTotalItems(response.data.total || 0);
      } catch (error) {
        console.error("Error fetching menu", error);
      }
    };
    fetchMenu();
  }, [currentPage]);

  // Функции для работы с корзиной
  const addToCart = (item) => {
    setCart((prevCart) => {
      const updatedCart = prevCart.some((cartItem) => cartItem.id === item.id)
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

  const updateQuantity = (id, delta) => {
    setCart((prevCart) => {
      const updatedCart = prevCart
        .map((item) =>
          item.id === id ? { ...item, quantity: item.quantity + delta } : item
        )
        .filter((item) => item.quantity > 0);

      localStorage.setItem("cart", JSON.stringify(updatedCart));
      return updatedCart;
    });
  };

  // Функции для модального окна
  const openModal = (dish) => {
    setSelectedDish(dish);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setSelectedDish(null);
    setIsModalOpen(false);
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
      <h2 className="text-4xl font-bold text-center mb-10">Меню</h2>

      {/* Сетка блюд */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
        {menu.map((item) => {
          const cartItem = cart.find((cartItem) => cartItem.id === item.id);
          return (
            <div
              key={item.id}
              className="bg-white rounded-lg shadow-lg overflow-hidden"
            >
              <img
                src={`${process.env.REACT_APP_API_GATEWAY_URL}/menu/images/${item.image_url.split("images/")[1]}`}
                alt={item.name}
                className="w-full h-48 object-cover cursor-pointer"
                onClick={() => openModal(item)} // Открываем модальное окно при клике
              />
              <div className="p-4 text-center">
                <h3 className="text-lg font-semibold">{item.name}</h3>
                <p className="text-gray-500">{item.description}</p>
                <p className="text-lg font-bold mt-2">${item.price}</p>

                {/* Управление количеством на карточке */}
                {cartItem ? (
                  <div className="flex justify-center items-center mt-3">
                    <button
                      onClick={() => updateQuantity(item.id, -1)}
                      className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-l"
                    >
                      -
                    </button>
                    <span className="mx-3 text-lg font-bold">{cartItem.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, 1)}
                      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r"
                    >
                      +
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => addToCart(item)}
                    className="mt-3 bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                  >
                    Добавить в корзину
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Пагинация */}
      {/* Добавьте код пагинации при необходимости */}

      {/* Модальное окно */}
      {isModalOpen && selectedDish && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white rounded-lg overflow-hidden w-11/12 md:w-2/3 lg:w-1/2">
            <div className="p-5">
              <h2 className="text-2xl font-bold mb-4">{selectedDish.name}</h2>
              <img
                src={`${process.env.REACT_APP_API_GATEWAY_URL}/menu/images/${selectedDish.image_url.split("images/")[1]}`}
                alt={selectedDish.name}
                className="w-full h-auto object-cover mb-4"
              />
              <p className="text-gray-500 mb-4">{selectedDish.description}</p>
              <p className="text-lg font-bold mb-4">${selectedDish.price}</p>

              {/* Управление количеством в модальном окне */}
              {cart.find((cartItem) => cartItem.id === selectedDish.id) ? (
                <div className="flex justify-center items-center mt-3">
                  <button
                    onClick={() => updateQuantity(selectedDish.id, -1)}
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-l"
                  >
                    -
                  </button>
                  <span className="mx-3 text-lg font-bold">
                    {cart.find((cartItem) => cartItem.id === selectedDish.id)?.quantity || 0}
                  </span>
                  <button
                    onClick={() => updateQuantity(selectedDish.id, 1)}
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r"
                  >
                    +
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => addToCart(selectedDish)}
                  className="mt-3 bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                >
                  Добавить в корзину
                </button>
              )}

              <button
                onClick={closeModal}
                className="mt-5 bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MenuList;