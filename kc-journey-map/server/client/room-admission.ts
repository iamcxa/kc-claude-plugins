import { journeyFetch, journeyApi, type HumanContext } from './api'

export class RoomAdmissionError extends Error {
 constructor(public sourceRoom: string, public category: string, public denied: boolean) { super(`Room ${sourceRoom} unavailable (${category}). Original room retained.`) }
}
export async function verifyRoomAdmission(roomId: string, context: HumanContext, signal: AbortSignal) {
 const response = await journeyFetch(journeyApi('/auth/entry?' + new URLSearchParams({ room: roomId })), { signal: AbortSignal.any([signal, AbortSignal.timeout(8000)]) })
 const result = await response.json()
 if (!response.ok) throw new RoomAdmissionError(roomId, result.category || 'host_unavailable', response.status === 401 || response.status === 403 || response.status === 404)
 if (result.room !== roomId || result.memberId !== context.member || result.backendId !== context.backend || result.verifiedHumanSignInAt !== context.signInAt) throw new RoomAdmissionError(roomId, 'identity_changed', true)
}

export const sourceAdmissionLost = (error: unknown, roomId: string) => error instanceof RoomAdmissionError && error.denied && (error.sourceRoom === roomId || ['identity_changed', 'authority_denied', 'human_sign_in_required', 'session_expired', 'human_revalidation_due', 'member_denied'].includes(error.category))
