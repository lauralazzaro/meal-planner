import { useState } from 'react';
import { addItemToList } from '../api/shoppingLists';

function ShoppingListCard({ list, ingredients, onDeleteList, onDeleteItem, onItemAdded }) {
  const [ingredientId, setIngredientId] = useState('');
  const [freeTextName, setFreeTextName] = useState('');
  const [freeTextCategory, setFreeTextCategory] = useState('');
  const [quantity, setQuantity] = useState('');

  async function handleAddFromPool(event) {
    event.preventDefault();
    await addItemToList(list.id, {
      ingredient_id: parseInt(ingredientId),
      quantity: quantity ? parseInt(quantity) : null,
    });
    setIngredientId('');
    setQuantity('');
    onItemAdded();
  }

  async function handleAddFreeText(event) {
    event.preventDefault();
    await addItemToList(list.id, {
      name: freeTextName,
      shopping_category: freeTextCategory,
    });
    setFreeTextName('');
    setFreeTextCategory('');
    onItemAdded();
  }

  return (
    <div style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}>
      <h2>
        {list.name}
        <button onClick={onDeleteList}>Elimina lista</button>
      </h2>

      <ul>
        {list.items.map((item) => (
          <li key={item.id}>
            {item.name} {item.quantity && `x${item.quantity}`} ({item.shopping_category})
            <button onClick={() => onDeleteItem(item.id)}>Rimuovi</button>
          </li>
        ))}
      </ul>

      <form onSubmit={handleAddFromPool}>
        <select value={ingredientId} onChange={(e) => setIngredientId(e.target.value)} required>
          <option value="">Scegli dal pool</option>
          {ingredients.map((ing) => (
            <option key={ing.id} value={ing.id}>{ing.name}</option>
          ))}
        </select>
        <input
          type="number"
          placeholder="Quantità"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />
        <button type="submit">Aggiungi dal pool</button>
      </form>

      <form onSubmit={handleAddFreeText}>
        <input
          type="text"
          placeholder="Nome (es. Detersivo)"
          value={freeTextName}
          onChange={(e) => setFreeTextName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Categoria"
          value={freeTextCategory}
          onChange={(e) => setFreeTextCategory(e.target.value)}
          required
        />
        <button type="submit">Aggiungi voce libera</button>
      </form>
    </div>
  );
}

export default ShoppingListCard;