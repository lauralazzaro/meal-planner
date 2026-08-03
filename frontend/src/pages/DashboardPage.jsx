import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getWeeklyPlans } from '../api/weeklyPlans';
import { getDishLabel } from '../utils/dish';
import {
  DAY_KEYS_BY_JS_INDEX,
  DAY_LABELS,
  MEAL_LABELS,
  MEALS,
} from '../constants/labels';

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Buongiorno';
  if (hour < 18) return 'Buon pomeriggio';
  return 'Buonasera';
}

function DashboardPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPlans();
  }, []);

  async function loadPlans() {
    try {
      const data = await getWeeklyPlans();
      setPlans(data);
    } catch (err) {
      setError('Errore nel caricamento del piano settimanale.');
    } finally {
      setLoading(false);
    }
  }

  const today = DAY_KEYS_BY_JS_INDEX[new Date().getDay()];
  const activePlan = plans.find((p) => p.is_default) || plans[0];
  const todaysEntries = activePlan
    ? activePlan.dishes.filter((entry) => entry.day_of_week === today)
    : [];

  return (
    <div className="dashboard">
      <section className="dashboard-hero">
        <div>
          <h2>{getGreeting()}!</h2>
          <p>
            {activePlan
              ? `Hai ${todaysEntries.length} ${todaysEntries.length === 1 ? 'pasto pianificato' : 'pasti pianificati'} per oggi (${DAY_LABELS[today]}).`
              : 'Non hai ancora un piano settimanale impostato.'}
          </p>
        </div>
        <div className="dashboard-hero-actions">
          <Link to="/weekly-plans" className="primary">
            <span className="material-symbols-outlined">calendar_month</span>
            Piano settimanale
          </Link>
          <Link to="/shopping-lists" className="secondary">
            <span className="material-symbols-outlined">shopping_cart</span>
            Lista della spesa
          </Link>
        </div>
      </section>

      <h3 className="dashboard-section-title">I pasti di oggi</h3>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {!loading && !activePlan && (
        <div className="dashboard-empty-plan">
          <p>
            Non hai ancora nessun piano settimanale. <Link to="/weekly-plans">Creane uno</Link> per vedere qui i pasti di oggi.
          </p>
        </div>
      )}

      {!loading && activePlan && (
        <div className="meal-grid">
          {MEALS.map((type) => {
            const entry = todaysEntries.find((e) => e.meal_type === type);
            return (
              <div key={type} className={`meal-card${entry ? '' : ' empty'}`}>
                <span className={`meal-card-badge ${type.toLowerCase()}`}>
                  {MEAL_LABELS[type]}
                </span>
                {entry ? (
                  <>
                    <h4>{getDishLabel(entry.dish)}</h4>
                    {entry.dish.comment && <p>{entry.dish.comment}</p>}
                  </>
                ) : (
                  <>
                    <p>Nessun piatto pianificato.</p>
                    <Link to="/weekly-plans">Pianifica</Link>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default DashboardPage;
