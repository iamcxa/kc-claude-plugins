import { events } from './store.js';

export async function sendMail(to, subject, body) {
  events.push({ op: 'mail', to, subject, body });
}
