export function assetUploadId(fileName: string) {
	return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}-${fileName.replace(/[^a-zA-Z0-9._-]/g, '_')}`
}
