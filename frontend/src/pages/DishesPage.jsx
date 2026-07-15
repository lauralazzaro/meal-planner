import { useState, useEffect } from 'react';
import { getDishes, createDish, deleteDish } from '../api/dishes';
import { getIngredients } from '../api/ingredients';

function DishesPage() {
  const [dishes, setDishes] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [label, setLabel] = useState('');
  const [comment, setComment] = useState('');
  const [mainIngredientId, setMainIngredientId] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadDishes();
    loadIngredients();
  }, []);

  async function loadDishes() {
    try {
      const data = await getDishes();
      setDishes(data);
    } catch (err) {
      setError('Errore nel caricamento dei piatti.');
    }
  }

  async function loadIngredients() {
    const data = await getIngredients();
    setIngredients(data);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');

    try {
      await createDish(label, comment, mainIngredientId);
      setLabel('');
      setComment('');
      setMainIngredientId('');
      loadDishes();
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Ingrediente non trovato.');
      } else {
        setError('Errore durante la creazione.');
      }
    }
  }

  async function handleDelete(id) {
    await deleteDish(id);
    loadDishes();
  }

  return (
    <div>
      <h1>Piatti</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Label"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
        />
        <select
          value={mainIngredientId}
          onChange={(e) => setMainIngredientId(e.target.value)}
          required
        >
          <option value="">Seleziona ingrediente principale</option>
          {ingredients.map((ingredient) => (
            <option key={ingredient.id} value={ingredient.id}>
              {ingredient.name}
            </option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
        <button type="submit">Aggiungi</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <ul>
        {dishes.map((dish) => (
          <li key={dish.id}>
            {dish.label} — {dish.main_ingredient?.name}
            <button onClick={() => handleDelete(dish.id)}>Elimina</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default DishesPage;