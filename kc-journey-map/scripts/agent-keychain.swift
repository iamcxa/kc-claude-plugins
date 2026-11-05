import Foundation
import Security
import Darwin

func reply(_ value: [String: Any]) {
 if let data = try? JSONSerialization.data(withJSONObject: value), let text = String(data: data, encoding: .utf8) { print(text); fflush(stdout) }
}
func fail(_ category: String, _ status: OSStatus? = nil) { reply(["ok": false, "category": category, "osStatus": status as Any]) }
func valid(_ value: String) -> Bool { value.range(of: "^[A-Za-z0-9_-]{1,128}$", options: .regularExpression) != nil }
guard let line = readLine(), let data = line.data(using: .utf8), let open = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
 let backend = open["backendId"] as? String, let installation = open["installationId"] as? String, valid(backend), valid(installation), let lockPath = open["lockPath"] as? String else { fail("protected_store_invalid"); exit(1) }
let fd = Darwin.open(lockPath, O_CREAT | O_RDWR | O_NOFOLLOW, S_IRUSR | S_IWUSR)
var info = stat()
guard fd >= 0, fstat(fd, &info) == 0, info.st_uid == geteuid(), (info.st_mode & 0o077) == 0, (info.st_mode & S_IFMT) == S_IFREG else { fail("protected_lock_denied"); exit(1) }
guard flock(fd, LOCK_EX | LOCK_NB) == 0 else { fail("installation_busy"); exit(1) }
defer { flock(fd, LOCK_UN); Darwin.close(fd) }
reply(["ok": true])
while let line = readLine() {
 guard let data = line.data(using: .utf8), let request = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
  let action = request["action"] as? String, let slot = request["slot"] as? String, UUID(uuidString: slot) != nil else { fail("protected_store_invalid"); continue }
 let query: [String: Any] = [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: "dev.kc-journey-map.agent.v1", kSecAttrAccount as String: backend + ":" + installation + ":" + slot, kSecAttrSynchronizable as String: false]
 if action == "delete" {
  let status = SecItemDelete(query as CFDictionary)
  if status == errSecSuccess || status == errSecItemNotFound { reply(["ok": true]) } else { fail("protected_store_unavailable", status) }
 } else if action == "get" {
  var read = query; read[kSecReturnData as String] = true; read[kSecMatchLimit as String] = kSecMatchLimitOne
  var found: CFTypeRef?; let status = SecItemCopyMatching(read as CFDictionary, &found)
  if status == errSecSuccess, let bytes = found as? Data, let value = String(data: bytes, encoding: .utf8) { reply(["ok": true, "value": value]) }
  else { fail("protected_store_unavailable", status) }
 } else if action == "put", let value = request["value"] as? String, let bytes = value.data(using: .utf8), bytes.count < 65536 {
  var create = query; create[kSecValueData as String] = bytes; create[kSecAttrAccessible as String] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
  let status = SecItemAdd(create as CFDictionary, nil)
  if status == errSecSuccess { reply(["ok": true]) } else { fail("protected_store_unavailable", status) }
 } else { fail("protected_store_invalid") }
}
