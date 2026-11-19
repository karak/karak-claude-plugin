import { useState } from 'react';

async function postWithRetry(url, attempts = 3) {
  for (let i = 0; i < attempts; i++) {
    try {
      const r = await fetch(url, { method: 'POST', signal: AbortSignal.timeout(5000) });
      return r;
    } catch (e) {
      // timeout or network error: retry
    }
  }
  throw new Error('payment failed');
}

export function PayButton({ orderId }) {
  const [state, setState] = useState('idle'); // idle | sending | done | error
  const onClick = async () => {
    setState('sending');
    try {
      await postWithRetry(`/orders/${orderId}/pay`);
      setState('done');
    } catch {
      setState('error');
    }
  };
  return <button onClick={onClick}>Pay</button>;
}
