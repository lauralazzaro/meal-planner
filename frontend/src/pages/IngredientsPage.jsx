import { useState, useEffect } from 'react';
import { getIngredients, createIngredient, deleteIngredient } from '../api/ingredients';
import { CATEGORIES, CATEGORY_LABELS } from '../constants/labels';

function IngredientsPage() {
  const [ingredients, setIngredients] = useState([]);
  const [nextCursor, setNextCursor] = useState(null);
  const [hasNext, setHasNext] = useState(false);
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [error, setError] = useState('');

  async function loadIngredients(cursor) {
    try {
      const data = await getIngredients(cursor);
      setIngredients((prev) => (cursor ? [...prev, ...data.items] : data.items));
      setNextCursor(data.next_cursor);
      setHasNext(data.has_next);
    } catch (err) {
      setError('Errore nel caricamento degli ingredienti.');
    }
  }

  useEffect(() => {
    loadIngredients();
  }, []);

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
    // Remove locally instead of refetching: a delete never changes the
    // sort order of the remaining items, so this stays correct without
    // touching nextCursor/hasNext or losing pages already loaded.
    setIngredients((prev) => prev.filter((ingredient) => ingredient.id !== id));
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
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          required
        >
          <option value="">Scegli categoria</option>
          {CATEGORIES.map((key) => (
            <option key={key} value={key}>{CATEGORY_LABELS[key]}</option>
          ))}
        </select>
        <button type="submit">Aggiungi</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <ul>
        {ingredients.map((ingredient) => (
          <li key={ingredient.id}>
            {ingredient.name} — {CATEGORY_LABELS[ingredient.shopping_category]}
            <button onClick={() => handleDelete(ingredient.id)}>Elimina</button>
          </li>
        ))}
        {hasNext && (
          <button onClick={() => loadIngredients(nextCursor)}>Carica altri</button>
        )}
      </ul>
    </div>
  );
}

export default IngredientsPage;