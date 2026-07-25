import { useState, useEffect } from 'react';
import {
  getShoppingLists,
  createShoppingList,
  deleteShoppingList,
  addItemToList,
  deleteItemFromList,
} from '../api/shoppingLists';
import { getIngredients } from '../api/ingredients';
import ShoppingListCard from '../components/ShoppingListCard'

function ShoppingListsPage() {
  const [lists, setLists] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [newListName, setNewListName] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadLists();
    loadIngredients();
  }, []);

  async function loadLists() {
    try {
      const data = await getShoppingLists();
      setLists(data);
    } catch (err) {
      setError('Errore nel caricamento delle liste.');
    }
  }

  async function loadIngredients() {
    const data = await getIngredients();
    setIngredients(data.items);
  }

  async function handleCreateList(event) {
    event.preventDefault();
    await createShoppingList(newListName);
    setNewListName('');
    loadLists();
  }

  async function handleDeleteList(id) {
    await deleteShoppingList(id);
    loadLists();
  }

  async function handleDeleteItem(listId, itemId) {
    await deleteItemFromList(listId, itemId);
    loadLists();
  }

  return (
    <div>
      <h1>Liste della spesa</h1>

      <form onSubmit={handleCreateList}>
        <input
          type="text"
          placeholder="Nome nuova lista"
          value={newListName}
          onChange={(e) => setNewListName(e.target.value)}
          required
        />
        <button type="submit">Crea lista</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {lists.map((list) => (
        <ShoppingListCard
          key={list.id}
          list={list}
          ingredients={ingredients}
          onDeleteList={() => handleDeleteList(list.id)}
          onDeleteItem={(itemId) => handleDeleteItem(list.id, itemId)}
          onItemAdded={loadLists}
        />
      ))}
    </div>
  );
}

export default ShoppingListsPage;