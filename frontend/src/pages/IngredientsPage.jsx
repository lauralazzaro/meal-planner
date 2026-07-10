import { useState, useEffect } from 'react';
import { getIngredients, createIngredient, deleteIngredient } from '../api/ingredients';

function IngredientsPage() {
  const [ingredients, setIngredients] = useState([]);
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [error, setError] = useState('');

  // Runs once, right after the component first appears on screen
  useEffect(() => {
    loadIngredients();
  }, []);

  async function loadIngredients() {
    try {
      const data = await getIngredients();
      setIngredients(data);
    } catch (err) {
      setError('Errore nel caricamento degli ingredienti.');
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');

    try {
      await createIngredient(name, category);
      setName('');
      setCategory('');
      loadIngredients(); // refresh the list after adding
    } catch (err) {
      if (err.response?.status === 409) {
        setError('Ingrediente già esistente.');
      } else {
        setError('Errore durante la creazione.');
      }
    }
  }

  async function handleDelete(id) {
    await deleteIngredient(id);
    loadIngredients(); // refresh the list after deleting
  }

  return (
    <div>
      <h1>Ingredienti</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Nome"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Categoria"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          required
        />
        <button type="submit">Aggiungi</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <ul>
        {ingredients.map((ingredient) => (
          <li key={ingredient.id}>
            {ingredient.name} — {ingredient.shopping_category}
            <button onClick={() => handleDelete(ingredient.id)}>Elimina</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default IngredientsPage;