export function getDishLabel(dish) {
  return dish.label || dish.main_ingredient?.name || 'Piatto senza nome';
}
