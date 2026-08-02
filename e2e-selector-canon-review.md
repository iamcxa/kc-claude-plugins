---
title: Re-decide the canonical selector grammar — it has been declared for three months and adopted zero times
status: validation
source: captain approval 2026-07-25, escalated out of e2e-selector-lint-gate when the codemod spike showed the canonical form is unsupported by the target apps
product: e2e-pipeline
sprint: S1
started: 2026-07-25T13:47:31Z
completed:
verdict: PASSED
worktree:
issue:
pr: pr-merge:123:artifact-v1:46326e65931dc616a539f9ab1af1aea1e7f8e652db465e10ab3634cbbba56fe3
design: required
id: rd55vfpddtyvsbfqxqecj6cx
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiW3JkXSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvOTVhMzdiYzU5YTI5ZGI5M2FiZmZmYWI0OTA2NDE0NjcxZDcxYmJjNi9lMmUtc2VsZWN0b3ItY2Fub24tcmV2aWV3Lm1kKSIsImJhc2UiOiJtYWluIiwiYmFzZV9vaWQiOiIxZDZkMGQwMmQ0YjBkNmM4NGVhYzA4MTNlNjk2MmM2Nzc0ZTY1MmI3IiwiYm9keSI6IkxhbmRzIHRoZSBjYXB0YWluLWFwcHJvdmVkIGBlMmUtc2VsZWN0b3ItY2Fub24tcmV2aWV3YCBydWxpbmcgKDIwMjYtMDctMjUpLCB3aGljaCB3YXMgYnVpbHQsIGdhdGUtcmV2aWV3ZWQgb25jZSBhdCBpbXBsZW1lbnRhdGlvbiBsZXZlbCwgdGhlbiBwYXJrZWQgdW5tZXJnZWQgZm9yIHRocmVlIG1vbnRocy4gUmViYXNlZCBhY3Jvc3MgNjQgY29tbWl0cyBvZiBgbWFpbmAsIHZhbGlkYXRlZCBmcmVzaCwgYW5kIGV4dGVuZGVkIGJ5IHR3byBkZWZlY3RzIHRoYXQgb25seSB0aGUgcmUtdmFsaWRhdGlvbiBmb3VuZC5cblxuU2NoZWR1bGVkIGFzIGBlMmUtcGlwZWxpbmUvUzFgIGl0ZW0gKioyYSoqIOKAlCBhIHByZXJlcXVpc2l0ZSBFTSBydWxlZCBpbiBhaGVhZCBvZiAjODgsIGJlY2F1c2UgIzg4IGFza3MgdGhlIGNvbXBpbGVyIHRvIGVuZm9yY2UgdGhlIHNhbWUgZ3JhbW1hciBhcyBgc2NyaXB0cy9saW50LW1hcHBpbmcuc2hgLCBhbmQgb24gYG1haW5gIHRoYXQgc2NyaXB0IHN0aWxsIGJhbnMgdGhlIHR3byBmb3JtcyB0aGlzIHJ1bGluZyBkZWxldGVkLiBJbXBsZW1lbnRpbmcgIzg4IGZpcnN0IHdvdWxkIGhhdmUgaW5zdGFsbGVkIGEgY2FwdGFpbi1yZWplY3RlZCBiYW4gYXQgYSBib3VuZGFyeSB0aGF0IHJlZnVzZXMuXG5cbiMjIFdoYXQgdGhlIHJ1bGluZyB3YXNcblxuUmVsZWFzZSAyLjcuMCBkZWNsYXJlZCBgW3JvbGU9XCI8cj5cIl1bYXJpYS1sYWJlbD1cIjx2PlwiXWAgdGhlIGNhbm9uaWNhbCBgc2VsZWN0b3I6YCBmb3JtIGFuZCBiYW5uZWQgdGhlIFBsYXl3cmlnaHQtc2hhcGVkIGByb2xlPVhbbmFtZT1cIllcIl1gLiBNZWFzdXJlZCBvdmVyIDMyIHJlYWwgbWFwcGluZyBmaWxlcyB0aHJlZSBtb250aHMgbGF0ZXI6XG5cbnwgZm9ybSB8IG9jY3VycmVuY2VzIHxcbnwtLS18LS0tfFxufCBjYW5vbmljYWwgYFtyb2xlPVwi4oCmXCJdW2FyaWEtbGFiZWw9XCLigKZcIl1gIHwgKiowKiogfFxufCBiYW5uZWQgYHJvbGU9WFtuYW1lPVwi4oCmXCJdYCB8ICoqMiwxODMqKiB8XG5cblRoZSBjYXVzZSBpcyBzdHJ1Y3R1cmFsLCBub3QgZGlzY2lwbGluYXJ5OiB0aGUgQ1NTIGZvcm0gbWF0Y2hlcyB0d28gKmxpdGVyYWwgYXR0cmlidXRlcyosIGFuZCBgYXJpYS1sYWJlbGAgYXBwZWFycyBvbiB-Mi44JSBvZiBjb21wb25lbnRzIGluIHRoZSB0YXJnZXQgYXBwLCBzbyB0aGUgbWFwcGVyIGNhbm5vdCBlbWl0IGl0LiBNZWFud2hpbGUgYGNvbXBpbGVyL2xpYi9zZWxlY3Rvci10cmFuc2xhdGUuanNgIGVtaXRzICoqYnl0ZS1pZGVudGljYWwgb3V0cHV0KiogZm9yIHRoZSBiYW5uZWQgYW5kIGNhbm9uaWNhbCBmb3JtcyDigJQgdGhlIGNvbXBpbGVyIG5ldmVyIGV4ZWN1dGVkIHRoZSBzZWxlY3RvciwgaXQgdHJhbnNsYXRlZCBpdC4gVGhlIDIsMTgzIFwidmlvbGF0aW9uc1wiIHdlcmUgbmV2ZXIgYnJva2VuIG9uIHRoZSBjb21waWxlZCBwYXRoLlxuXG5TbzogZGVsZXRlIGxpbnQgQ0xBU1MgMSwgZml4IENMQVNTIDMsIGFkZCBhIGB0ZXh0PVZgIHRyYW5zbGF0aW9uIGJyYW5jaCwgZGVtb3RlIGBbcm9sZV1bYXJpYS1sYWJlbF1gIHRvIHNlY29uZGFyeSwgZG9jdW1lbnQgdGhlIHVuZG9jdW1lbnRlZCBgY3NzX3NlbGVjdG9yOmAgZmllbGQsIGFuZCBjb2xsYXBzZSAxMyBwcm9zZSByZXN0YXRlbWVudHMgdG8gb25lIGF1dGhvcml0eS4gKipaZXJvIG1hcHBpbmcgZmlsZXMgbWlncmF0ZS4qKiBDTEFTU0VTIDIgKGA-PiBudGg9YCksIDQgKGA6aGFzLXRleHQoYCksIDUgKGZpbmQtc3ViY29tbWFuZC1hcy1hLXNlbGVjdG9yLXZhbHVlKSBzdGF5IGJhbm5lZC5cblxuIyMgTWVhc3VyZWQgZWZmZWN0IG9uIHRoZSByZWFsIGNvcnB1c1xuXG5gc2NyaXB0cy9saW50LW1hcHBpbmcuc2hgIG92ZXIgYC9Vc2Vycy9rZW50L1Byb2plY3QvY2FybG92ZS8uY2xhdWRlL2UyZS9tYXBwaW5ncy8qLnlhbWxgOlxuXG58IHwgbWFwcGluZ3MgZmFpbGluZyB8IGZpbmRpbmdzIHxcbnwtLS18LS0tfC0tLXxcbnwgYG1haW5gIHwgKio1IC8gNSoqIHwgMTcyIGByb2xlLWF0dHJgLCA0OCBgdGV4dD1gLCAzOSBgPj5udGhgIHxcbnwgdGhpcyBicmFuY2ggfCAqKjIgLyA1KiogfCAzOSBgPj5udGhgIG9ubHkgfFxuXG5UaGUgcmVzaWR1ZSBpcyBleGNsdXNpdmVseSBDTEFTUyAyLCB3aGljaCBpcyBjb3JyZWN0bHkgc3RpbGwgYmFubmVkIGFuZCB3aG9zZSBtaWdyYXRpb24gaXMgb3duZWQgYnkgdGhlIGBlMmUtbnRoLWNob3JkLXdpZGVuaW5nYCBlbnRpdHkuIE5vdGhpbmcgdW4tYmFubmVkIHN0aWxsIGZhaWxzLlxuXG4jIyBUd28gZGVmZWN0cyB0aGUgcmUtdmFsaWRhdGlvbiBmb3VuZCBhbmQgZml4ZWRcblxuKioxLiBgdGV4dD1gIHZhbHVlcyBuZWVkaW5nIHNuYXBzaG90IGVzY2FwaW5nIGVtaXR0ZWQgYSBwYXR0ZXJuIHRoYXQgZ3JlcHMgbm90aGluZy4qKiBUaGUgcXVvdGUgZGV0ZWN0aW9uIG9ubHkgZmlyZWQgd2hlbiB0aGUgcXVvdGUgd2FzIGNoYXJhY3RlciAwLCBzbyBhIG1pZC12YWx1ZSBxdW90ZSBmZWxsIHRocm91Z2ggdG8gYSBuYWl2ZSB3cmFwLiBQcm9iZWQgbGl2ZSBhZ2FpbnN0IGFnZW50LWJyb3dzZXIgMC4zMi4wICsgQ2hyb21lIGZvciBUZXN0aW5nIDE1MSwgYW4gYWNjZXNzaWJsZSBuYW1lIHJlbmRlcnMgd2l0aCBKU09OLXN0eWxlIGVzY2FwaW5nOlxuXG5gYGBcbi0gYnV0dG9uIFwiU2F2ZVxcXCJOb3dcIiBbcmVmPWUxXVxuLSBidXR0b24gXCJiYWNrXFxcXHNsYXNoXCIgW3JlZj1lMV1cbmBgYFxuXG5gdGV4dD1TYXZlXCJOb3dgIHByb2R1Y2VkIGBcIlNhdmVcIk5vd1wiYCwgd2hpY2ggaXMgbm90IGEgc3Vic3RyaW5nIG9mIHRoYXQuIE5vdyByZWZ1c2VkIChudWxsIC0-IGRvY3VtZW50ZWQgYF9wb2xsX3Zpc2libGVgIGZhbGxiYWNrKSByYXRoZXIgdGhhbiByZXByb2R1Y2luZyB0aGUgZXNjYXBpbmcsIGJlY2F1c2UgbWlycm9yaW5nIGEgdGhpcmQtcGFydHkgcmVuZGVyaW5nIGNvbnZlbnRpb24gd291bGQgcmVzdCB0aGUgYnJhbmNoIGludmFyaWFudCBvbiBzb21ldGhpbmcgdGhpcyBtb2R1bGUgY2Fubm90IHBpbi4gQ29zdHMgdGhlIGNvcnB1cyBub3RoaW5nIOKAlCBubyBjb3JwdXMgYHRleHQ9YCB2YWx1ZSBjYXJyaWVzIGVpdGhlciBjaGFyYWN0ZXIuXG5cbioqMi4gVGhlIGdyYW1tYXIgYXV0aG9yaXR5IGRpZCBub3Qgc2F5IHRoYXQgaXRzIG93biBwcmltYXJ5IGZvcm0gY2Fubm90IGJlIGNsaWNrZWQuKiogUHJvYmVkIGxpdmU6IGBpcyB2aXNpYmxlICdyb2xlPWJ1dHRvbltuYW1lPVwiQWxwaGFCdG5cIl0nYCBhbmQgYGlzIHZpc2libGUgJ3RleHQ9QWxwaGFCdG4nYCBib3RoIHJldHVybmVkICoqZmFsc2UqKiBhZ2FpbnN0IGEgZml4dHVyZSB3aG9zZSBzbmFwc2hvdCBzaG93ZWQgdGhlIGJ1dHRvbiwgd2hpbGUgYFtyb2xlPVwiYnV0dG9uXCJdW2FyaWEtbGFiZWw9XCLpgJrnn6VcIl1gIGFuZCBgaDFgIHJldHVybmVkICoqdHJ1ZSoqLiBTbyBmb3JtcyAyIGFuZCAzIHJlc29sdmUgb24gdGhlIHRyYW5zbGF0ZWQgdmlzaWJpbGl0eSBwYXRoIG9ubHk7IGFuIGVsZW1lbnQgdGhleSBsb2NhdGUgdGhhdCBhIHN0ZXAgYWxzbyBjbGlja3Mgb3IgZmlsbHMgbmVlZHMgYGNzc19zZWxlY3RvcjpgLiBgQ0xBVURFLm1kYCBub3cgc2F5cyBzby4gSXQgZmFpbHMgbG91ZCB1bmRlciBgZTJlLXRlc3QtcnVubmVyYCBSdWxlIDEsIG5vdCBzaWxlbnRseSDigJQgd2hpY2ggaXMgd2h5IGJvdGggZm9ybXMgYmVsb25nIGluIFJ1bGUgMSdzIE5BVElWRSBsaXN0IHJhdGhlciB0aGFuIG1lcmVseSBiZWluZyBkcm9wcGVkIGZyb20gaXRzIGJhbm5lZCBsaXN0LlxuXG5BbHNvIGNvcnJlY3RlZCB0d28gY2xhaW1zIGluIHRoYXQgc2VjdGlvbiB0aGF0IGhhZCBkcmlmdGVkOiB0aGUgYTExeSBwYXR0ZXJuIGlzIGVtaXR0ZWQgYXQgYGNvZGVnZW4uanM6MTc2NmAsIG5vdCAxNTcyLCBhbmQgdGhlIGdlbmVyYXRlZCBgX3BvbGxfc25hcHNob3RfY29udGFpbnNgIGhlbHBlciBpcyBhIEJhc2ggc3Vic3RyaW5nIHRlc3QsIG5vdCBhIGBncmVwIC1GYC5cblxuIyMgUmViYXNlIGZpZGVsaXR5XG5cbjcgb2YgMTQgZmlsZXMgYWxzbyBjaGFuZ2VkIG9uIGBtYWluYCBzaW5jZSBtZXJnZS1iYXNlIGA3NTIxNTQ2YDsgMiBjb25mbGljdGVkLiBgbWFpbmAgaGFkIHRlbXBsYXRlZCBoYXJkY29kZWQgYGFnZW50LWJyb3dzZXJgIGludG8gYHt7YnJvd3Nlcl9jb21tYW5kfX1gIOKAlCByZXNvbHV0aW9uIHRvb2sgdGhlIGJyYW5jaCdzICoqY29udGVudCoqIGFuZCBgbWFpbmAncyAqKnRlbXBsYXRpbmcqKiwgYW5kIGluIGBlMmUtdGVzdC1ydW5uZXIubWRgIENyaXRpY2FsIFJ1bGVzIGtlcHQgYG1haW5gJ3MgaXRlbSA4IChuZXdlciB0cmFjZS1maW5hbGl6YXRpb24gYmVoYXZpb3IpIHdpdGggdGhlIGJyYW5jaCdzIGl0ZW0gOS4gTm8gYmFyZSBgYWdlbnQtYnJvd3NlcmAgd2FzIHJlaW50cm9kdWNlZCB3aGVyZSB0aGUgZmlsZSdzIG93biBjb250cmFjdCByZXF1aXJlcyB0aGUgcnVudGltZSB3cmFwcGVyLlxuXG5CZWNhdXNlIHRoZSByZWJhc2UgbW92ZWQgZXZlcnkgbGluZSB0aGUgb3JpZ2luYWwgZmFsc2lmaWVyIHdhcyBhbmNob3JlZCBvbiwgYm90aCBsb2FkLWJlYXJpbmcgbWVhc3VyZW1lbnRzIHdlcmUgKipyZS1kZXJpdmVkIG9uIHRoZSByZWJhc2VkIHRyZWUqKiwgbm90IGNhcnJpZWQgb3ZlcjpcblxuLSAqKkV2YWwtZmFsbGJhY2sgZ3VhcmQsIHNlbnRlbmNlIGdyYW51bGFyaXR5OioqIDEzIGd1YXJkZWQgc2VudGVuY2VzIG9uIGBvcmlnaW4vbWFpbmAsIDEzIG9uIEhFQUQsICoqMCByZW1vdmVkIC8gMCBhZGRlZCoqLCBieXRlLWlkZW50aWNhbC4gKEEgbGluZS1sZXZlbCBncmVwIGdpdmVzIGEgZmFsc2UgcG9zaXRpdmUgaGVyZSBiZWNhdXNlIG9uZSBwaHlzaWNhbCBsaW5lIHBhY2tzIHRoZSBmb3JtLWxpc3Qgc2VudGVuY2UgdG9nZXRoZXIgd2l0aCB0aHJlZSBndWFyZGVkIHNlbnRlbmNlcy4pXG4tICoqQnJhbmNoIG1hcHBpbmcsIDMxMCB1bmlxdWUgY29ycHVzIHNlbGVjdG9yczoqKiA0NyBgdGV4dD1gIHNlbGVjdG9ycyBtb3ZlIHRvIGBfcG9sbF9zbmFwc2hvdF9jb250YWluc2A7ICoqMCBub24tdGV4dCBzZWxlY3RvcnMgY2hhbmdlIGJyYW5jaCoqIOKAlCBjb25maXJtaW5nIHRoZSBgcm9sZT1gIGJyYW5jaGVzIGFyZSBiZWhhdmlvdXJhbGx5IHVudG91Y2hlZCwgbm90IG1lcmVseSBhYnNlbnQgZnJvbSB0aGUgZGlmZi4gQnJhbmNoIHNlbGVjdGlvbiBkZXBlbmRzIG9uIHRoZSB0cmFuc2xhdG9yJ3MgcmV0dXJuIHZhbHVlLCBzbyBgY29kZWdlbi5qc2AgYmVpbmcgYWJzZW50IGZyb20gdGhlIGRpZmYgaXMgbmVjZXNzYXJ5IGJ1dCBub3Qgc3VmZmljaWVudCwgd2hpY2ggaXMgd2h5IHRoaXMgaXMgbWVhc3VyZWQgcmF0aGVyIHRoYW4gYXNzZXJ0ZWQuXG5cbiMjIFZhbGlkYXRpb24gZXZpZGVuY2VcblxuLSAqKkxlbnNlczoqKiBjb3JyZWN0bmVzcyAoZXhlcmNpc2UtYmFzZWQsIGxpdmUgYnJvd3NlcikgUEFTUyDCtyBzaWxlbnQtZmFpbHVyZSAxIE1FRElVTSBmaW5kaW5nLCAqKmNvbmZpcm1lZCBhcyBhIHJlYWwgZGVmZWN0IGFuZCBmaXhlZCoqIChpdGVtIDEgYWJvdmUpLCAxIGNvcnJlY3RseSBpZGVudGlmaWVkIGFzIHByZS1leGlzdGluZyBhbmQgb3V0IG9mIHNjb3BlIMK3IG1hbmlmZXN0L2JhY2stY29tcGF0IFBBU1MgKG5vIGBwbHVnaW4uanNvbmAgLyBgbWFya2V0cGxhY2UuanNvbmAgLyByZWxlYXNlLWNvbmZpZyAvIHNraWxsLWZyb250bWF0dGVyIHN1cmZhY2UgdG91Y2hlZDsgYHZlcnNpb24tcGFyaXR5LWNoZWNrLnNoYCBhbmQgYHNraWxsLWZyb250bWF0dGVyLWxpbnQuc2hgIGJvdGggZ3JlZW4sIDM1LzM1IHNraWxscykuIE5vdCBmaXJlZCwgd2l0aCB0aGUgc3VyZmFjZXMgbmFtZWQ6IG5vIG5ldyBvciBjaGFuZ2VkIHR5cGUsIG5vIGxvY2svYXN5bmMvc2hhcmVkLXN0YXRlLCBubyBwcm9jZXNzIG9yIGhhbmRsZSBsaWZlY3ljbGUsIG5vIGF1dGggb3IgdHJ1c3QgYm91bmRhcnksIG5vIHdvcmtmbG93IGZpbGUuXG4tICoqRGlmZiBjb3ZlcmFnZToqKiAqKjEwMCUqKiDigJQgKioxNyBvZiAxNyoqIGFkZGVkIGV4ZWN1dGFibGUgbGluZXMgY292ZXJlZDsgYmFyIGlzIDg1JS4gKEFuIGVhcmxpZXIgcmV2aXNpb24gb2YgdGhpcyBib2R5IHNhaWQgXCI1OC81OFwiOyB0aGF0IHdhcyB3cm9uZyBhbmQgdGhlIEVNIGdhdGUgY2F1Z2h0IGl0LiA1OCBpcyB0aGUgKnRvdGFsKiBhZGRlZC1saW5lIGNvdW50IG9mIGBzZWxlY3Rvci10cmFuc2xhdGUuanNgLCBvZiB3aGljaCA0MSBhcmUgdGhlIGRvYyBibG9jayBhbmQgaW5saW5lIGNvbW1lbnRzIOKAlCBOb2RlJ3MgbGNvdiBlbWl0cyBgREFgIHJlY29yZHMgZm9yIGNvbW1lbnQgbGluZXMgdG9vLCBzbyBmaWx0ZXJpbmcgb24gXCJpbnN0cnVtZW50ZWRcIiBkaWQgbm90IGV4Y2x1ZGUgdGhlbS4gTnVtZXJhdG9yIGFuZCBkZW5vbWluYXRvciBjb3VsZCBub3QgYm90aCBiZSA1OC4pIFRoZSBvbmx5IGFkZGVkIGV4ZWN1dGFibGUgbG9naWMgaXMgaW4gYHNlbGVjdG9yLXRyYW5zbGF0ZS5qc2A7IGBsaW50LW1hcHBpbmcuc2hgJ3MgYWRkZWQgbm9uLWNvbW1lbnQgbGluZXMgYXJlIGFsbCBgdXNhZ2UoKWAgc3RyaW5ncyBhbmQgaXRzIGxvZ2ljIGh1bmtzIGFyZSBkZWxldGlvbnMuXG4tICoqQWR2ZXJzYXJpYWw6KiogNCBjbGFpbS1icmVha2luZyBlZGl0cyBpbiBzY3JhdGNoIGNvcGllcywgYWxsIGdvIHJlZCBhcyBzcGVjaWZpZWQg4oCUIHJlbW92ZSB0aGUgcmVnZXggcmVmdXNhbCAoNy8yNSByZWQpLCByZXZlcnQgdGhlIGNob3JkIHN0cmlwICg3LzI1IHJlZCksIHJlbW92ZSB0aGUgbmV3IGVzY2FwaW5nIHJlZnVzYWwgKDIvMjcgcmVkKSwgcmVzdG9yZSBsaW50IENMQVNTIDEgKGNvcnB1cyAyLzUgLT4gKio1LzUqKiBmYWlsaW5nLCB3aGljaCBpcyBBQy0xJ3Mgb3duIHN0YXRlZCBmYWxzaWZpZXIpLlxuLSAqKkNyb3NzLW1vZGVsOioqIHJ1biBvbiB0aGUgZXhhY3QgaGVhZCwgZmluZGluZ3MgZGlzcG9zaXRpb25lZCBhdCB0aGUgZ2F0ZS5cbi0gKipFMkU6KiogQUMtMyBleGVyY2lzZWQgYWdhaW5zdCBhICoqbGl2ZSoqIGBhZ2VudC1icm93c2VyIDAuMzIuMGAgKyBDaHJvbWUgZm9yIFRlc3RpbmcgMTUxIHNuYXBzaG90IGRyaXZlbiB0aHJvdWdoIHRoZSBwbHVnaW4ncyBvd24gb3duZWQgYnJvd3NlciBydW50aW1lIChpc29sYXRlZCBuYW1lc3BhY2UsIENocm9tZSBmb3IgVGVzdGluZyBwaW5uZWQsIGNsb3NlZCBhZnRlcikuIDkgY2FzZXMsIGluY2x1ZGluZyBhIG5lZ2F0aXZlIGNvbnRyb2wgKGB0ZXh0PU5vdFByZXNlbnRgIG11c3Qgbm90IGhpdCkgYW5kIHRoZSByZWdleCByZWZ1c2FsLCB2ZXJpZmllZCB0aHJvdWdoIGJvdGggYSByZWFsIGBncmVwIC1GYCBzdWJwcm9jZXNzIGFuZCB0aGUgZXhhY3QgQmFzaCBzdWJzdHJpbmcgdGVzdCBjb2RlZ2VuIGVtaXRzLlxuXG5GdWxsIHN1aXRlICoqODkxIC8gODkyIHBhc3NpbmcqKiwgMTYxIHN1aXRlcywgMSBza2lwcGVkIChvcHQtaW4gYnJvd3NlciB0ZXN0KS4gU2NvcGVkIGBzZWxlY3Rvci10cmFuc2xhdGUudGVzdC5qc2AgMjcvMjcuIEJpb21lIGNsZWFuLCBTaGVsbENoZWNrIGAtUyBlcnJvcmAgY2xlYW4sIGBiYXNoIC1uYCBjbGVhbi5cblxuT25lIGZ1bGwtc3VpdGUgcnVuIHN1cmZhY2VkIGFuIHVucmVsYXRlZCBmYWlsdXJlIGluIGBjb21waWxlci90ZXN0L3RyYWNlLWZpbmFsaXphdGlvbi50ZXN0LmpzYDsgaXNvbGF0ZWQgdG8gbG9hZC1mbGFraW5lc3MgKDQ5LzQ5IHN0YW5kYWxvbmUgb24gYm90aCB0aGlzIGJyYW5jaCBhbmQgY2xlYW4gYG1haW5gLCBncmVlbiBvbiBmdWxsLXN1aXRlIHJlLXJ1bikgYW5kIGZpbGVkIGFzICMxMjIgcmF0aGVyIHRoYW4gd3JpdHRlbiBvZmYuXG5cbiMjIEFDIGRpc3Bvc2l0aW9uXG5cbnwgQUMgfCB2ZXJkaWN0IHwgZXZpZGVuY2UgfFxufC0tLXwtLS18LS0tfFxufCBBQy0xIOKAlCB0aGUgcnVsZSBhbmQgdGhlIGNvcnB1cyBhZ3JlZSB8ICoqUEFSVElBTCoqLCBhcyB0aGUgZW50aXR5J3Mgb3duIGN5Y2xlLTEgcmUtc2NvcmUgY29ycmVjdGVkIGl0IHwgY29ycHVzIDUvNSAtPiAyLzUgZmFpbGluZzsgcmVzaWR1ZSBleGNsdXNpdmVseSBzdGlsbC1iYW5uZWQgQ0xBU1MgMiB8XG58IEFDLTIg4oCUIHRoZSBleGVjdXRhYmlsaXR5IGNsYWltIGlzIGdvbmUgYW5kIGNhbm5vdCBzaWxlbnRseSByZXR1cm4gfCAqKlBBU1MqKiB8IHN3ZWVwIGZvciBgc2lsZW50bHkgbWlzaGFuZGxlZGAgLyBgZXhlY3V0ZWQgZGlyZWN0bHlgIGNsZWFuIG91dHNpZGUgYENIQU5HRUxPRy5tZGAgKHJlbGVhc2UtcGxlYXNlLW93bmVkKSB8XG58IEFDLTMg4oCUIHRoZSBgdGV4dD1gIGNsYXNzIHJlc29sdmVzIHwgKipQQVNTKiogfCBsaXZlLXNuYXBzaG90IHJvdW5kLXRyaXAsIGV4ZXJjaXNlZCBub3QgcmVhZCB8XG5cbiMjIFJlc2lkdWFscywgbmFtZWQgcmF0aGVyIHRoYW4gZml4ZWRcblxuLSBUaGUgc2FtZSBieXRlLWZpZGVsaXR5IGNsYXNzIGluIHRoZSAqKnByZS1leGlzdGluZyoqIGByb2xlPWAgYnJhbmNoIGZvciBhIGJhY2tzbGFzaCB2YWx1ZSDigJQgb3V0c2lkZSB0aGlzIGVudGl0eSdzIGFwcHJvdmVkIHNjb3BlLCBmaWxlZCBhcyAqKiMxMjEqKiB0b2dldGhlciB3aXRoIHRoZSBhbHJlYWR5LXRyYWNrZWQgYGUyZS1yZWdleC1wcmVmaXgtZmFsc2UtbWF0Y2hgIGluc3RhbmNlLCBzaW5jZSBvbmUgY29udmVudGlvbiBzaG91bGQgY2xvc2UgYm90aC5cbi0gVGhlIDM5IGA-PiBudGg9YCBjb3JwdXMgb2NjdXJyZW5jZXMgc3RheSBncmFuZGZhdGhlcmVkOyBvd25lciBlbnRpdHkgYGUyZS1udGgtY2hvcmQtd2lkZW5pbmdgIGlzIHN0aWxsIGBiYWNrbG9nYCB3aXRoIG5vIGlzc3VlIGFuZCBubyBzcHJpbnQsIHNvIHRoYXQgZGVmZXJyYWwgaGFzIG5vIGxhbmRpbmcgZGF0ZS4gQ2FsbGVkIG91dCBiZWNhdXNlIFwiZGVmZXJyZWQgdG8gWFwiIHJlYWRzIHN0cm9uZ2VyIHRoYW4gaXQgaXMuXG4tIFRoZSBkZXYtZmxvdyBzdGF0ZSBlbnRpdHkgYW5kIG1lYXN1cmVtZW50LWxlZGdlciByb3cgY2Fubm90IGJlIHdyaXR0ZW4gZnJvbSB0aGlzIHdvcmtzcGFjZTogaXQgaXMgYSBzdGF0ZSAqKm5vbi1ob2xkZXIqKiwgYW5kIHRoZSBgcHItbWVyZ2VgIGxpZmVjeWNsZSBob29rcyBmYWlsIGNsb3NlZCBvZmYgdGhlIHJlZ2lzdGVyZWQgaG9sZGVyLCB3aGljaCBhIGNvbmN1cnJlbnQgYGtjLXByLWZsb3dgIHNlc3Npb24gb3ducy4gU2FtZSBib3VuZGFyeSBhcyAjMTA0IC8gIzEwNyAvICMxMTAuIEJvb2trZWVwaW5nIGlzIG93ZWQgdG8gdGhlIGhvbGRlcjsgdGhlIGNvZGUgaXMgbm90IGJsb2NrZWQgb24gaXQuXG5cbiMjIE5vdCBpbmRlcGVuZGVudGx5IHJlcHJvZHVjaWJsZSBmcm9tIHRoaXMgbWFjaGluZVxuXG5UaGUgZW50aXR5J3MgMjYvMzIgYW5kIDE5LzMyIHdpZGVyLWNvcnB1cyBmaWd1cmVzLCBhbmQgY3ljbGUgMidzIDI5NS84MS1zZWxlY3RvciBjb3VudHMuIFRoZSByZWFjaGFibGUgY29ycHVzIGlzIDUgbWFwcGluZyBmaWxlcyAvIDMxMCB1bmlxdWUgc2VsZWN0b3JzLCBzbyB0aGUgZmFsc2lmaWVyIGRpcmVjdGlvbiBpcyBjb25maXJtZWQgbG9jYWxseSBidXQgbm90IHRob3NlIGV4YWN0IG1hZ25pdHVkZXMuXG5cblxuLS0tXG5cbiMjIEVNIHZhbGlkYXRpb24gZ2F0ZSDigJQgdmVyZGljdCBgbmFycm93YCwgY29uZGl0aW9ucyBkaXNjaGFyZ2VkXG5cblZhbGlkYXRpb24gd2FzIGFjY2VwdGVkIHdpdGggdGhyZWUgYmxvY2tpbmcgY29uZGl0aW9ucyBhbmQgdHdvIG5vbi1ibG9ja2luZy4gQWxsIGRpc2NoYXJnZWQ7IENJIHJlLWNvbmZpcm1lZCBncmVlbiBvbiB0aGUgcmVzdWx0aW5nIGV4YWN0IGhlYWQsIHBlciB0aGUgb2JzZXJ2ZWQtZ3JlZW4tcGVyLWNvbW1pdCBydWxlLlxuXG58IHwgY29uZGl0aW9uIHwgZGlzcG9zaXRpb24gfFxufC0tLXwtLS18LS0tfFxufCBDMSB8IHByZS1tZXJnZSBsZWRnZXIgcm93IG9uIHRoZSBwcm9kdWN0IGJyYW5jaCwgYHByZW1lcmdlYCB2ZXJpZmllZCB8IGBkb2NzL2Rldi9sZWRnZXIuY3N2YCByb3cgZm9yIGByZDU1dmZwZGR0eXZzYmZxeHFlY2o2Y3hgLCB2ZXJpZmllciByZXR1cm5zICoqYGxlZGdlcjpleGFjdGAqKiwgb25lIGluc2VydGlvbiwgbm8gb3RoZXIgYnl0ZSBtb3ZlZCB8XG58IEMyIHwgc3dlZXAgdGhlIGxhc3QgYGJhbm5lZCBQbGF5d3JpZ2h0YCByZXN0YXRlbWVudHMgfCBgdGVzdC9pbnRlZ3JhdGlvbi1zbW9rZS5zaGAg4oCUIGl0IHRvbGQgdGhlIG9wZXJhdG9yIHRoZSBtYXBwZXIgXCJtYXkgc3RpbGwgYmUgZW1pdHRpbmcgUGxheXdyaWdodC1zdHlsZSBzZWxlY3RvcnNcIiBvbiAqYW55KiBsaW50IGZhaWx1cmUsIHdoaWNoIGFmdGVyIHRoaXMgY2hhbmdlIGlzIHRoZSBtYXBwZXIgZG9pbmcgdGhlIGNvcnJlY3QgdGhpbmcgfFxufCBDMyB8IHRlbGwgdGhlICoqcHJvZHVjZXIqKiB0byBlbWl0IGBjc3Nfc2VsZWN0b3I6YCBmb3IgY2xpY2thYmxlIGZvcm1zIHwgYGFnZW50cy9lMmUtbWFwcGVyLm1kYCDCpyBTZWxlY3RvciBQcmlvcml0eSArIFJ1bGUgOC4gVGhpcyBjaGFuZ2UgcHJvbW90ZXMgZm9ybSAyIHRvIHRoZSBkZWZhdWx0IGZvciBpbnRlcmFjdGl2ZSBlbGVtZW50czsgdGhlIGNhdmVhdCB0aGF0IG1ha2VzIHRoZSBwcm9tb3Rpb24gc2FmZSBsaXZlZCBvbmx5IGluIHRoZSByZWFkZXIncyBmaWxlIHxcbnwgQzUgfCBmaXggdGhlIGNvdmVyYWdlIGxhYmVsOyBnaXZlIHRoZSBudGgtY2hvcmQgcmVzaWR1YWwgYW4gYXJ0aWZhY3QgfCBsYWJlbCBjb3JyZWN0ZWQgYWJvdmU7IGZpbGVkICoqIzEyNCoqIHxcblxuKipFTSBvdmVycnVsZWQgbWUgb24gdGhlIGxlZGdlciByb3csIGNvcnJlY3RseS4qKiBJIGhhZCBhcmd1ZWQgbm8gcm93IHdhcyBvd2VkIGJlY2F1c2UgdGhpcyB3b3Jrc3BhY2UgaXMgYSBzdGF0ZSBub24taG9sZGVyLiBUaGF0IGNvbmZsYXRlZCB0d28gZGlmZmVyZW50IHdyaXRlczogdGhlIGVudGl0eSBzdGF0ZSBsaXZlcyBvbiBgc3BhY2Vkb2NrLXN0YXRlL2RldmAgYmVoaW5kIHRoZSBob2xkZXItZ2F0ZWQgYHByLW1lcmdlYCBob29rcywgYnV0IGBkb2NzL2Rldi9sZWRnZXIuY3N2YCBpcyBhIGdpdC10cmFja2VkIGZpbGUgaW4gdGhlIGNvZGUgdHJlZSBhbmQgdGhlIFJFQURNRSBwdXRzIGl0cyByb3cgb24gdGhlICpwcm9kdWN0IGJyYW5jaCouIFRoZSBzZW50aW5lbHMgYXJlIHRoZSByZXF1aXJlZCBwcmUtbWVyZ2UgYXJ0aWZhY3QsIG5vdCBhbiB1bmZpbmFsaXphYmxlIGRlZmVjdCDigJQgc2tpcHBpbmcgdGhlIHJvdyB3b3VsZCBoYXZlIGxlZnQgdHdvIGJsb2NrZXJzIGluc3RlYWQgb2Ygb25lLCBhbmQgd291bGQgaGF2ZSBkcm9wcGVkIHRoaXMgc2Vzc2lvbidzIGRpc3BhdGNoIGFuZCB0b2tlbiBldmlkZW5jZSBhdCB0aGUgbGFzdCBib3VuZGFyeSB3aGVyZSBpdCBzdGlsbCBleGlzdHMuIE15IHByZWNlZGVudCBjbGFpbSB3YXMgYWxzbyB3cm9uZzogIzEwNC8jMTA3LyMxMTAgYXJlIGlzc3Vlcywgbm90IFBScywgc28gdGhleSB3ZXJlIG5ldmVyIGRldi1mbG93IGVudGl0aWVzIGNhcnJ5aW5nIHJvd3MuXG5cbioqQSBtZWFzdXJlbWVudCBJIHJlcG9ydGVkIHdhcyB3cm9uZyBhbmQgdGhlIGd1YXJkIGNhdWdodCBpdC4qKiBJIHRvbGQgdGhlIGdhdGUgdGhlIGV2YWwtZmFsbGJhY2sgZmFsc2lmaWVyIHN0aWxsIHJlYWQgMC8wIGFmdGVyIGEgdGVybWlub2xvZ3kgZWRpdC4gSXQgZGlkIG5vdCDigJQgbXkgc2NyaXB0IHJlYWQgYGdpdCBzaG93IEhFQUQ6PGZpbGU-YCwgc28gaXQgbWVhc3VyZWQgdGhlIGxhc3QgY29tbWl0IHJhdGhlciB0aGFuIHRoZSB1bmNvbW1pdHRlZCBlZGl0IHVuZGVyIHRlc3QuIFJlLWRlcml2ZWQgYWdhaW5zdCB0aGUgd29ya2luZyB0cmVlLCB0aGUgZWRpdCAqZGlkKiB0b3VjaCBhIHByb3RlY3RlZCBzZW50ZW5jZTogYFJ1bGUgMTRgJ3MgYm9sZCBsZWFkLWluIGNsb3NlcyB3aXRoIGAqKmAgYW5kIG5vIGZvbGxvd2luZyBzcGFjZSwgc28gaXQgc2hhcmVzIGEgc2VudGVuY2Ugd2l0aCBcImRvIE5PVCBmYWxsIGJhY2sgdG8gZXZhbFwiLiBUaGF0IHJlbmFtZSBpcyAqKnJldmVydGVkKio7IHRoZSBndWFyZCBvdXRyYW5rcyB0aGUgY2xlYW51cC4gVGhlIGZhbHNpZmllciBub3cgcmVhZHMgdGhlIHdvcmtpbmcgdHJlZSwgYW5kIHRoZSBjb3JyZWN0ZWQgcmVzdWx0IGlzIDEzIGd1YXJkZWQgc2VudGVuY2VzIG9uIGBvcmlnaW4vbWFpbmAsIDEzIGluIHRoZSB0cmVlLCAqKjAgcmVtb3ZlZCAvIDAgYWRkZWQqKi5cblxuUmVzaWR1YWwgZnJvbSB0aGF0OiBgZTJlLXRlc3QtcnVubmVyLm1kYCBDcml0aWNhbCBSdWxlIDE0IHN0aWxsIGNhbGxzIHRoZSBzdXJ2aXZpbmcgc2V0IFwiQmFubmVkIFBsYXl3cmlnaHQgZm9ybXNcIiBpbiBpdHMgbGVhZC1pbi4gSXRzIG93biBib2R5IGVudW1lcmF0ZXMgdGhlIGNvcnJlY3QgdGhyZWUgY2xhc3Nlcywgc28gaXQgbWlzbmFtZXMgdGhlIGNhdGVnb3J5IHdpdGhvdXQgbWlzc3RhdGluZyBpdHMgbWVtYmVyc2hpcCwgYW5kIGNoYW5naW5nIGl0IGJlbG9uZ3MgdG8gdGhlIGd1YXJkJ3Mgb3duZXIuXG5cbioqU3RyZW5ndGhlbmVkLCBwZXIgRU06KiogXCIwIG5vbi10ZXh0IHNlbGVjdG9ycyBjaGFuZ2UgYnJhbmNoXCIgaG9sZHMgKipieSBjb25zdHJ1Y3Rpb24qKiwgbm90IGp1c3QgYnkgY29ycHVzIGNvdW50IOKAlCB0aGUgbmV3IGJsb2NrIGlzIGEgcHVyZSBpbnNlcnRpb24gKGArNTgvLTBgKSBnYXRlZCBvbiBgL150ZXh0PS9gIGFuZCBwbGFjZWQgYWZ0ZXIgZXZlcnkgb3RoZXIgYnJhbmNoLiBUaGF0IGFyZ3VtZW50IGRvZXMgbm90IGRlY2F5IHdpdGggdGhlIGNvcnB1cywgd2hpY2ggYWxzbyBtb290cyB0aGUgZWFybGllciBjYXZlYXQgYWJvdXQgdW5yZXByb2R1Y2libGUgd2lkZXItY29ycHVzIG1hZ25pdHVkZXMuXG5cbioqQmxvY2tzIHRoZSBuZXh0IHRhc2ssIG5vdCB0aGlzIG1lcmdlOioqIG1lcmdpbmcgdGhpcyByZXRpcmVzIHRoZSBiYW4gdGhhdCAjODgncyBmaWxlZCB0ZXh0IHVzZXMgYXMgaXRzIHByZW1pc2Ug4oCUICM4OCdzIHJlcHJvIHN0ZXAgMSBvZmZlcnMgYHJvbGU9aGVhZGluZ1tuYW1lPVwi5rSX6LuK6aCQ57SEXCJdYCBhcyBhIGJhbm5lZCBleGFtcGxlIGFuZCBzdGVwIDUgZXhwZWN0cyBgZXhpdCAyYCB3aXRoIGEgYHJvbGUtYXR0cmAgZmluZGluZywgbmVpdGhlciBvZiB3aGljaCByZXByb2R1Y2VzIGFmdGVyd2FyZHMuIEEgd29ya2VyIHN0YXJ0aW5nIGZyb20gdGhlIGZpbGVkIHRleHQgd291bGQgaW1wbGVtZW50IHRoZSByZXRpcmVkIGJhbiBpbnRvIGEgY29tcGlsZXIgZ2F0ZSwgd2hpY2ggaXMgdGhlIHNhbWUgZGVmZWN0IHdpdGggZW5mb3JjZW1lbnQgYmVoaW5kIGl0LiAjODggaXMgcmUtc2hhcGVkIGJlZm9yZSBkaXNwYXRjaC5cblxuXG5bcmRdKC9pYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMvYmxvYi85NWEzN2JjNTlhMjlkYjkzYWJmZmZhYjQ5MDY0MTQ2NzFkNzFiYmM2L2UyZS1zZWxlY3Rvci1jYW5vbi1yZXZpZXcubWQpIiwiYm9keV9zaGEyNTYiOiI3MjNjMTZjMThiMGZkN2MxMGJhNjM4N2RhODg3N2Q2MzNiZGE4MmRiMjcxY2Y0Yjc0YzNhN2E3NjllNjI0NmI4IiwiZGlmZl9zaGEyNTYiOiI1Mzg0NTZmZTJhYTNiMGRjYjk0ZmJlYTNmNWVjMGFiYmEzYWY5NTVkZTk5M2RmOTg0MzEzZWQwNmY1MGI3ZmM3IiwiaGVhZCI6ImZpeC9lMmUtc2VsZWN0b3ItY2Fub24tbGFuZCIsImhlYWRfb2lkIjoiMTI2MDY2ZjUzZDJkYzBlMWIwYTdjOWY0MDAxOTg0YzhlODI1NDQ2NiIsImxpdmVfcGF0aCI6ImUyZS1zZWxlY3Rvci1jYW5vbi1yZXZpZXcubWQiLCJyZXBvIjoiaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zIiwidGl0bGUiOiJmaXgoZTJlLXBpcGVsaW5lKTogbGFuZCB0aGUgc2VsZWN0b3ItZ3JhbW1hciBjYW5vbiBjb3JyZWN0aW9uIn0
---

## Problem

Release 2.7.0 (2026-05-04, "Selector Grammar Alignment") established
`[role="<r>"][aria-label="<v>"]` as the canonical selector form, banned the Playwright
`role=X[name="Y"]` alternative in `scripts/lint-mapping.sh`, instructed `agents/e2e-mapper.md`
to emit the canonical form, and restated the rule across 13 markdown files.

Measured over 32 unique real mapping files, the newest written **today, 2026-07-25** — almost
three months after the canon shipped:

| Form | Occurrences |
|---|---|
| canonical `[role="…"][aria-label="…"]` | **0** |
| banned `role=X[name="…"]` | **2,183** |
| `data-testid` | 167 |
| `find role` subcommand | 1 |

This is not a corpus that predates the rule. Mappings generated today still emit the banned
form exclusively and the canonical form not once. **The canon has been in force for three
months and has changed nothing.**

The reason is structural, not disciplinary. In the primary target app, `aria-label` appears in
21 of 741 component files (2.8%) and an explicit `role=` in 10 (1.3%). CSS
`[role="button"][aria-label="Save"]` matches two *literal attributes*; for a plain
`<button>Save</button>` it matches nothing. The mapper cannot emit the canonical form for
elements that do not carry the attributes, so it emits what the accessibility tree gives it —
which is shaped like the banned form. Meanwhile Playwright's `role=X[name=Y]` matches the
*computed accessible name* and the *implicit* role, which is why it reads correctly off an a11y
snapshot even though agent-browser (CDP, not Playwright) then mishandles it at runtime.

So the pipeline is in the worst of both states: the form that describes what the mapper can see
does not execute, and the form that executes cannot describe what the mapper can see.

## Why this is the thesis of the whole programme in one artefact

An invariant was declared in prose — in a linter nothing calls, in an agent body, and in 13
restatements — and never placed at a boundary that could refuse. Three months later it is
provably not true, and nobody noticed, because nothing was ever in a position to notice.

## Notes for ideation

- Blocks [[e2e-selector-lint-gate]], which was pulled from sprint 1 on this finding. That entity
  as written would reject 26 of 32 mappings in favour of a form the apps structurally cannot
  support — it would break the pipeline rather than repair it. Do not restart it until this
  entity concludes.
- The candidate answers are visibly different in cost: `data-testid` already has 167 real uses
  but requires editing application source; the `find role|text` subcommand path matches what the
  mapper can observe but is a *subcommand*, not a `selector:` value, so adopting it is a mapping
  schema change (this is the same wall the codemod spike hit — 83 of its 198 refusals were bare
  `text=` for exactly this reason).
- Whatever is decided, the decision must land somewhere that can refuse it, or this recurs.
  Prefer the outcome that [[e2e-schema-contract]] can enforce over the one that reads best in
  CLAUDE.md.
- Before deciding, settle the empirical question the codemod spike could not: does the CSS form
  resolve against the real app at all? That needs a browser and a running target — a static
  read of selector text cannot answer it, and the spike said so explicitly rather than guessing.
- Check whether the mapper verifies that the selector it writes resolves. Exploration clicks via
  ephemeral `@ref` handles and then writes a separately derived selector string; nothing in
  `agents/e2e-mapper.md` requires confirming the written string matches anything. If so, that is
  the seam that let this run for three months.

---

## Decision — captain approved `narrow`, 2026-07-25

Three independent passes converged. The framing in the Problem section above was
half right and located the defect in the wrong place; the correction below is the
ruling.

**The defect is the executability premise, not the schema.** `compiler/lib/selector-translate.js`
emits byte-identical output for the canonical form (`:47-50`) and the banned form
(`:74-76`) — both become the a11y pattern `<role> "<name>"`, which `codegen.js:1572`
feeds to `_poll_snapshot_contains` for a `grep -Fq` against the accessibility
snapshot. **The compiler never executes the selector string; it translates it.** So
the 2,183 "violations" were never broken on the compiled path, and PR #8 chose a
syntax to satisfy a "must be directly executable" constraint that its own compiler
already contradicted.

### Empirical record (settled here, previously assumed by everyone)

Against a live `agent-browser` 0.21.4 and a fixture of three buttons — two with no
`role` and no `aria-label`, one with both:

```
- button "AlphaBtn" [ref=e1]        # no attributes; snapshot still emits role + computed name
- button "GammaLabel" [ref=e3]      # aria-label wins over text content
  - StaticText "GammaBtn"

grep -Fq 'button "AlphaBtn"'        # HIT
[role="button"][aria-label="Save"]  # count 0 against <button>Save</button>
find role button click --name BetaBtn   # clicks BetaBtn — matches the computed name
```

This settles the one condition the engineering-judgment review named as its single
point of risk: had the grep missed, the whole a11y path would have been broken for
97.2% of components and a schema rewrite would have been justified. It hit, so the
narrow route holds and its confidence rises from medium to high. The `aria-label`
line also shows the snapshot carries the *computed* accessible name — which is
exactly what `role=X[name="Y"]` encodes. The banned form was a faithful encoding of
the snapshot all along.

### Why it survived three months

PR #8 solved a real defect — issue #7 reproduced `is visible 'role=tab[name="Lineage"]'`
returning false, falling through to an `eval` fallback, and reporting a **false PASS**.
The fixes that actually solved it are `selector-translate.js` + `_poll_snapshot_contains`
and the Eval-Fallback Removal Policy. **Neither depends on the syntax choice, and
neither may be reverted** — see [[e2e-guard-eval-fallback-removal]].

The syntax ban was cargo cult layered on top. The only form issue #7 verified as
working was `[role="tab"]` — role only. PR #8 generalised that to the *combined*
`[role][aria-label]` form, which no live app ever exercised: its three runtime
verification checks were all deferred on a missing `SNOWFLAKE_ACCOUNT`, and the
review stage elevated "static contract review is equivalent to a runtime check"
into a standing principle. The 0-versus-2,183 measurement is the bill for that
substitution. PR #8 also filed `docs/ship-flow/todos/compiled-vs-llm-divergence-baseline.md`,
which predicted this exact divergence and was never run.

### Approved scope — zero mappings migrate

1. State in `CLAUDE.md` and `agents/e2e-mapper.md` that `selector:` is a
   plugin-internal locator DSL, not an agent-browser argument. Remove the
   executability claim.
2. Un-ban `role=X[name="Y"]` — delete `lint-mapping.sh` CLASS 1 or drop it to warn.
   Keep CLASSES 2, 4, 5.
3. Add a `text=V -> "V"` branch to `selector-translate.js`, fixing CLASS 3, which
   currently points at a form CLASS 5 forbids.
4. Demote `[role][aria-label]` to a secondary form, used only where the component
   genuinely carries `aria-label`.
5. Document the existing but unrecorded `css_selector:` field (read at
   `resolver.js:62`, required by the runtime_ref fill path) — today it is dead code
   for any mapping `/e2e-map` produces.
6. Collapse the rule's 13 restatements to one authority plus the translator.

Resolve while editing: `CLAUDE.md` Selector Priority §8 prescribes the very form §9
and lint CLASS 5 forbid; `agents/e2e-test-runner.md:550` calls `find …` the
"canonical NATIVE form" while five other files call it deprecated; the `CLAUDE.md`
v2 example writes `selector: 'data-testid="value"'`, which is missing its brackets
and is not valid CSS.

**AC-1 — the rule and the corpus agree.** A mapping written by `/e2e-map` against a
real app passes `lint-mapping.sh` without edits. Verified by: linting a freshly
generated mapping. Falsified by: restoring CLASS 1, which returns 26 of 32 corpus
mappings to failing.

**AC-2 — the executability claim is gone and cannot silently return.** No shipped
doc asserts `selector:` is executed directly. Verified by: grep across the plugin's
markdown for the claim. Falsified by: any surviving restatement.

**AC-3 — the `text=` class resolves.** The 83 corpus selectors refused by the codemod
spike as `text-engine-not-a-selector` translate to a snapshot pattern that greps.
Verified by exercising them against a real snapshot, not by reading the branch.

Path item 4 of the reviewed route — replacing raw `is visible` in the runner and
verifier with the compiler's snapshot-grep — moved to
[[e2e-guard-eval-fallback-removal]], which owns the divergence question.

## Stage Report: implementation

- DONE: `compiler/lib/selector-translate.js` — add the `text=V` branch.
  RED recorded (10 tests, 7 failing on the new behavior) before implementing;
  GREEN after — commit `4f72e49`. `compiler/test/selector-translate.test.js`
  exercises `text=AlphaBtn`/`text=GammaLabel` against the entity's own
  empirical-record snapshot fixture via a real `grep -F` subprocess (not a JS
  string compare) plus a negative control (`text=NotPresent` must NOT hit) —
  satisfies AC-3 by exercising, not by reading the branch.
- DONE: `scripts/lint-mapping.sh` — remove CLASS 1, fix CLASS 3.
  Both enforcement blocks deleted (kept CLASSES 2/4/5); header comment,
  `usage()`, and the two test fixtures/smoke script that quoted the old class
  list updated to match. Empirically re-verified against the 5 real carlove
  mapping files: 3/5 pass outright, the 2 remaining failures are exclusively
  `>> nth=N` (CLASS 2, still correctly banned) — zero failures from CLASS 1/3.
- DONE: Full suite once at the exit, after scoped tests are green.
  `npm test` (`node --test compiler/test/*.test.js`): 637/637 passing,
  including the 122 backward-compat `role=X[name=Y]` assertions in
  `codegen.test.js` (unchanged behavior — falsified by any edit to the
  existing role-form branches, which were not touched).
- DONE: Remove the executability claim.
  `CLAUDE.md` § Selector Priority now states `selector:` is a locator DSL
  translated by the compiler for `expect:`/visibility checks — and precisely
  scopes the one place that's still literal: `click`/`fill` pass the raw
  value to `agent-browser` unless `css_selector:` is set (verified by reading
  `codegen.js`'s click/fill cases, not assumed — see Summary). Same statement
  added to `agents/e2e-mapper.md`. AC-2 grep swept clean outside `CHANGELOG.md`
  (release-please-owned, not hand-edited per repo convention).
- DONE: Demote `[role][aria-label]`.
  Now priority item 4 in `CLAUDE.md` and `agents/e2e-mapper.md`, "use ONLY
  when the DOM genuinely carries a literal `aria-label`" — `role=<r>[name=…]`
  and `text=<v>` are the new items 2-3 (primary/native).
- DONE: Document `css_selector:`.
  `CLAUDE.md` § Selector Priority: field, read site (`resolver.js:62`), and
  both consumers (`click` eval-path, required for `runtime_ref` SC-1032
  sensitive fills) — traced from `codegen.js:1291,1343,1363`.
- DONE: Collapse the restatements.
  `CLAUDE.md` is the sole authority; `agents/e2e-mapper.md` and
  `references/common-patterns.md` now point at it (mapper.md keeps a short
  emit-order summary since it's a live agent prompt, not idle prose — its
  own executability/priority claims were still required to be correct
  in-place, not just cite elsewhere). `agents/e2e-flow-verifier.md`,
  `docs/ci-integration.md`, `docs/debugging.md`, `skills/e2e-compile/SKILL.md`,
  `skills/e2e-walkthrough/reference.md` corrected in place (small, table-row
  restatements). `CHANGELOG.md` left untouched (historical + release-please
  owned). See Summary for one deliberately-deferred file.
- DONE: Resolve the contradictions.
  CLAUDE.md §8/§9 resolved by the priority-list rewrite (bare `text=` no
  longer sits under the nth-chord/find-subcommand items). `e2e-flow-verifier.md`
  Critical Rule 9 and the `data-testid="value"'` example (`:324-325`) fixed.
  `e2e-test-runner.md:550` — narrow wording-only fix (dropped "canonical",
  clarified CLI-only scope); lines 548-561 (Rule 1c, Rule 2, the guarded
  Eval-Fallback Removal Policy) otherwise untouched per the Do-Not-Touch
  boundary.

### Summary

Code: `selectorToA11yPattern()` gained a `text=V` → `"V"` branch (RED→GREEN,
commit `4f72e49`), and `lint-mapping.sh` stopped banning `role=X[name=Y]`/bare
`text=` while keeping CLASS 2/4/5 (nth chord, has-text, find-subcommand-as-
value) banned. Docs: `CLAUDE.md` is now the single Selector Priority
authority; the false "selector: is executed directly / silently mishandled"
claim is gone from every live doc (commit `70926ed`). Zero mapping files
touched — verified via `git status` in the external carlove corpus used for
empirical checks.

One finding surfaced during implementation, not in the approved scope: the
"`selector:` is never executed directly" framing in the entity body is true
for `expect:`/visibility checks (`codegen.js:1572`) but **not** for `click`/
`fill` — those pass the raw `selector:` value straight to `agent-browser
click|fill` unless `css_selector:` is set (`codegen.js` click/fill cases,
unchanged, "Do NOT touch"). I wrote the CLAUDE.md claim scoped to what's
actually true rather than repeat the broader claim as given — restating a
false invariant is the exact defect class this entity exists to fix. Whether
`role=X[name=Y]`/`text=V` reliably resolve on the click/fill path was not
covered by this entity's browser spike (which tested a11y-grep and `find
role … click`, not `agent-browser click 'role=…'` directly) and is worth a
follow-up spike — possibly under [[e2e-guard-eval-fallback-removal]] or a new
entity, captain's call.

Also deliberately deferred: `agents/e2e-test-runner.md` still calls
`role=X[name=Y]`/bare `text=` "BANNED Playwright forms" at line 557 (inside
the guarded 548-561 Rule 2) and restates that at Critical Rules 9/601 and
observability line 491. Only line 550 was named in the contradiction list;
fixing 596/601 without touching the guarded Rule 2 would have split the file
against itself, so I left all four in place. Flagging for the captain rather
than silently leaving it invisible.

## Feedback Cycles

- Cycle 1: return — SO/EM gate; surface 2 commits / 14 files / +263-133 vs estimate none-declared (ideation recorded no appetite — a gap in this entity's own ideation, noted rather than back-filled); AC unchanged (scope not narrowed; the three findings are all inside approved scope).

### AC re-score — the FO's earlier scoring was wrong, corrected here

**AC-1 → PARTIAL** (was recorded PASS). The criterion reads "the rule and the corpus
agree". New lint moves the corpus from 6/32 passing to 13/32; **19 still fail**. That is
progress, not agreement. The residue is `>> nth=` (339 lines) and `has-text(` (25), both
correctly still banned — ownership of the nth residue sits with
[[e2e-nth-chord-widening]]. The hand-built login-page mapping that "passed" was written
to the very rules under test and could not have failed; it evidences that the lint
change works as intended, not that the criterion is met.

**AC-3 → PARTIAL** (was recorded PASS). The headline "81/81 translate, zero pass
through raw" is true by construction: `selector-translate.js:108` matches `^text=(.+)$`,
so a non-null return is guaranteed and the metric cannot go below 100%. Re-measured
against what the patterns can actually match: **28 of 81 compile to patterns that can
never match** — 10 regex forms (`text=/Every \d+h/` → `"/Every \d+h/"`) and 18 chorded
(`text=取消預約 >> nth=0` → the whole chord inside the quotes). The 6/6 live-snapshot
round-trip with a negative control stands and is real, but it exercised only the
plain-literal class.

The sharp edge: the new lint **passes** those 28, where old CLASS 3 refused them. This
commit removed a refusal without adding the matching translation — one fresh instance
of the exact defect class the entity exists to remove.

**AC-2 → PASS**, independently confirmed by the reviewer.

### Return list (closed — no redesign; do NOT re-open the un-ban, the demotion, or the premise correction)

1. **`compiler/lib/selector-translate.js` — make the `text=` branch refuse what it
   cannot faithfully translate.** Either mirror the literal-prefix extraction the
   `role=` branch already has at `:86-91`, or return `null` for regex and chorded forms
   so they take the documented fallback. Invariant to restore: **a non-null return is a
   pattern that can actually match.** Add the corpus regex and chorded cases to
   `selector-translate.test.js`.
2. **`agents/e2e-test-runner.md` — MOVE `role=<r>[name="<v>"]` and `text=<v>` into Rule
   1's NATIVE list at `:550`; do not merely delete them from Rule 2's banned list at
   `:557`.** Deleting alone leaves them matching neither rule, which re-opens the eval
   bypass. Then fix `:596` (it still says *prefer* `[role][aria-label]`, contradicting
   the demotion, and advises `find text "<v>"` as a selector value, which CLASS 5 bans)
   and `:601`'s form list. The earlier justification for leaving these — that they sit
   inside or adjacent to the guarded Eval-Fallback block — does not hold: `## Critical
   Rules` starts at `:584`, so `:596` and `:601` are 35-45 lines outside the guard at
   `:548-561`. Only `:557` is inside. Falsifier: `git diff` must show no change to any
   sentence containing "fall back to eval", "--allow-eval-fallback", or "eval bypass".
3. Nothing else. `codegen.js` stays untouched.

**Check the reviewer named that the FO missed:** `codegen.js` being absent from the diff
is necessary but not sufficient for "compiled behaviour unchanged". Branch selection
depends on the translator's return value, so every `text=` selector moved from the
`null → _poll_visible` fallback to `_poll_snapshot_contains` (`codegen.js:1572-1597`)
without that file changing a line. Any future translator change needs this check.

## Stage Report: implementation (cycle 2)

Correction round 1. Both return-list items addressed; the ruling was not re-opened.
Commit `15ffa84`, 3 files, +131-7. `codegen.js` untouched (verified in the diff).

- DONE: Return item 1 — make the `text=` branch refuse what it cannot faithfully translate.
  RED recorded first: 25 tests, 10 pass / **15 fail**, e.g. `non-null pattern
  "\"預約詳情 >> nth=0\"" for text=預約詳情 >> nth=0 must match "- text \"預約詳情\" [ref=e9]"`.
  GREEN 25/25. Chose **strip chords, refuse regex** — split rather than uniform,
  and the split is evidence-driven, not taste: I ran the `role=` branch and it
  emits `combobox` for `role=combobox >> nth=0` (a pattern that genuinely
  matches) but `^Save$` for `/^Save$/` and `a` for `/a|b/` (patterns `grep -F`
  can never match). So mirroring `:93-95` restores the invariant while mirroring
  `:86-91` would have **recreated** it. Regex therefore returns null and takes
  the documented `_poll_visible` fallback.
- DONE: Add the corpus regex and chorded cases to `selector-translate.test.js`.
  15 new assertions. The load-bearing one is `INVARIANT: every corpus text= shape
  either returns null or greps its own snapshot line` — it pairs each real corpus
  selector with the snapshot line `agent-browser` would emit and requires a
  non-null pattern to hit it through the same `grep -F` the runtime uses. Falsified
  by reverting the chord strip (the 5 chorded cases plus the invariant test go red);
  a bare count could not catch that, which is why the pairing is asserted.
- DONE: Return item 2 — MOVE the two forms into Rule 1 rather than delete from Rule 2.
  `role=<r>[name="<v>"]` and `text=<v>` added to Rule 1's NATIVE list at `:550`;
  Rule 2's list at `:557` reduced to `>> nth=N` / `has-text(` / find-subcommand-
  stored-as-selector-value. Coverage re-checked form by form: every form now matches
  exactly one rule, so nothing falls through to re-open the eval bypass. The
  `find …` split is disjoint, not a gap — Rule 1 covers direct interactive CLI
  invocation, Rule 2 covers it stored as a `selector:` value.
- DONE: Fix `:596` and `:601`'s form lists.
  `:596` no longer says *prefer* `[role][aria-label]` (it contradicted the demotion)
  and no longer advises `find text "<v>"` as a selector value (CLASS 5 bans it).
  `:601` edited **only** in its form-list sentence.
- DONE: Falsifier — no change to any sentence containing `fall back to eval`,
  `--allow-eval-fallback`, or `eval bypass`.
  Verified mechanically at sentence granularity: 13 guarded sentences, old vs new
  byte-identical, 0 removed / 0 added. A line-level grep reports a false positive
  because `:601` packs the form-list sentence and three guarded sentences onto one
  physical line; the sentence-level check is the one the falsifier specifies.
- DONE: Carry-forward branch-mapping re-check after Fix 1.
  Measured across 295 unique corpus selectors, comparing pre-entity baseline /
  round 1 / after-fix: **regex forms return to the `_poll_visible` baseline**
  (round 1 had wrongly routed them to snapshot-grep); **chorded stay on
  `_poll_snapshot_contains` but with a matchable pattern** (`"預約詳情 >> nth=0"`
  → `"預約詳情"`); plain literals move to snapshot-grep as intended; **0 non-text
  selectors change branch**, confirming the `role=` branches are behaviourally
  untouched, not merely absent from the diff.
- DONE: Full suite once at the exit.
  652/652 passing. Lint fixture contract re-verified unchanged: `native-css-mapping`
  exit 0, `legacy-playwright-mapping` exit 2.

### Summary

Both fixes landed in `15ffa84` without re-opening the un-ban, the demotion, or the
premise correction. The `text=` branch now refuses regex and strips chords, so a
non-null return is always a matchable pattern; `e2e-test-runner.md` Rules 1/2 were
rebalanced by moving the two native forms up rather than deleting them down, keeping
every form covered by exactly one rule.

Two notes for the gate. First, the chord strip is a deliberate **widening** — `>> nth=1`
becomes "any match" rather than "the second match". I judged this sound for an
existence assertion against the a11y snapshot (which does not carry the DOM duplicate
the chord exists to disambiguate) and it matches what the `role=` branch already does,
but it is a semantic choice, not a mechanical one, and worth a look. Note these
selectors still fail lint CLASS 2 regardless, so they are flagged either way.

Second, a scope-honesty note on the AC-3 numbers: the reviewer's corpus is 81 `text=`
values with 10 regex / 18 chorded; the corpus reachable from this machine
(`/Users/kent/Project/carlove`, 5 mapping files) has 48 with **20 chorded and 0 regex**.
So the chorded fix is verified against real corpus data, while the regex refusal is
verified by construction plus the reviewer's cited shape (`text=/Every \d+h/`) and four
synthesised regex shapes — not against local corpus instances, because there are none.
Flagging rather than implying both classes got the same grade of evidence.

### Cycle 1 accepted — gate verdict `proceed`, three record corrections applied here

**The chord-strip justification is replaced.** The implementing worker defended
`text=V >> nth=N` → `"V"` with an untested hypothesis (that the a11y snapshot does not
carry the DOM duplicate the chord disambiguates). The reviewer found a proof that needs
no snapshot, and it is confirmed: **every chorded `text=` value in the corpus is
`nth=0`** (corpus-wide chords are 220 at nth=0, 118 at nth=1, 1 at nth=2 — all the
non-zero ones are `role=` forms), and `selectorToA11yPattern`'s only call site is
`codegen.js:1572`, gated on `element-visible`/`active`. For an existence assertion at
index 0, "the first V exists" and "a V exists" are the same claim. So this is an
equivalence, not a widening. `references/common-patterns.md:55` adds that under React
Native Web `nth=0` is the *hidden* duplicate, so translating it away is arguably a
correction.

**One clause is withdrawn from the record**: that these selectors "still fail lint
CLASS 2 regardless, so they are flagged either way". It is true on paper and empty in
practice — `lint-mapping.sh` has zero references in the consuming repo's `.github` or
`.githooks`, and inside this plugin only `test/integration-smoke.sh` invokes it. Citing
an unenforced lint as mitigation is precisely the defect this entity was chartered to
name, so it must not survive as one.

**AC-3 provenance.** The worker disclosed, unprompted, that the corpus reachable from
its worktree held 48 `text=` values with 20 chorded and **0 regex**, so its regex
refusal rested on construction plus synthesised cases. That gap is closed from the
FO side: the wider corpus scan sees 81 values including **10 real regex forms**, all
verified to return `null` after the fix, and the reviewer independently re-ran the
measurement (11 null / 71 matchable / 0 non-null-but-dead).

**Residual, accepted rather than fixed:** `CLAUDE.md` § Selector Priority — the new
single authority — still does not state that `text=/regex/` is refused and falls back,
nor that `role=X[name=/Y/]` is supported. Two lines; not worth a third cycle. Carry as
a doc follow-up or land before merge at the captain's discretion.

**Spun out, not absorbed:** [[e2e-regex-prefix-false-match]] — the reviewer found that
`selector-translate.js:86-91` emits bare, unquoted substring greps for `role=` regex
values (`/holder.*關閉/` → `holder`, which `grep -F` matches inside `placeholder`).
Pre-existing, false-PASS direction, and therefore more serious than the nth widening.
Not caused by this entity and not fixed by it.

## Stage Report: implementation (cycle 3 — rebase and land)

Cycle 2 was gate-accepted `proceed` on 2026-07-25 and then parked unmerged for three
months. This cycle changed no ruling: it rebased the built work onto current `main`,
closed the recorded doc residual, and fixed two defects the fresh validation found.
Product PR: #123. Head `4fe0597`.

- DONE: Rebase across 64 commits. Merge-base `7521546`; fresh branch
  `fix/e2e-selector-canon-land` from `15ffa84`. Same 14 files, same +390/-136 as
  before the rebase — the resolution preserved intent rather than re-deciding it.
  7 files had changed on both sides; 2 conflicted. `main` had meanwhile templated
  hardcoded `agent-browser` into `{{browser_command}}` / `<browser_command>`, so both
  resolutions took the branch's **content** with `main`'s **templating**. In
  `e2e-test-runner.md` Critical Rules, kept `main`'s item 8 (browser completion follows
  auth mode — newer trace-finalization behavior) and took the branch's item 9.
- DONE: Rebase-fidelity measurement, because an auto-merge can drop newer content
  silently. Of **1,077 lines `main` added since merge-base** across the 7 overlapping
  files, exactly **2 are absent** on the branch, and both are the two documented
  intentional supersessions at the conflict sites. **0 accidental drops.**
- DONE: Re-derive cycle 2's eval-fallback falsifier, which was anchored on line numbers
  the rebase moved. Sentence granularity: **13 guarded sentences on `origin/main`, 13 on
  HEAD, 0 removed / 0 added, byte-identical.** (Line-level grep gives a false positive
  because one physical line packs the form-list sentence with three guarded sentences.)
- DONE: Re-derive the branch-mapping check on the rebased tree. 310 unique corpus
  selectors: **47 `text=` move to `_poll_snapshot_contains`, 0 non-text selectors change
  branch.** Confirms the `role=` branches are behaviourally untouched rather than merely
  absent from the diff — necessary because branch selection reads the translator's
  return value, so `codegen.js` being unchanged proves nothing on its own.
- DONE: Close the doc residual carried by the cycle-1 gate record (commit `03a8c6f`).
  `CLAUDE.md` § Selector Priority now states that `role=<r>[name=/re/]` is accepted via
  literal-prefix extraction (naming the substring false-match hazard and its owner
  entity) and that `text=/re/` is refused and takes the `_poll_visible` fallback.
  Also corrected two claims in the same section that had drifted: the a11y pattern is
  emitted at `codegen.js:1766`, not 1572, and the generated `_poll_snapshot_contains`
  helper is a Bash substring test, not a `grep -F`.
- DONE: Fix a defect this diff introduced, found by the silent-failure lens and then
  confirmed empirically (commit `4fe0597`). The `text=` branch's quote detection only
  fired when the quote was character 0, so a mid-value quote fell through to the naive
  wrap and emitted a pattern the snapshot can never contain — the near-miss the branch's
  own invariant forbids. Probed live against agent-browser 0.32.0 + Chrome for Testing
  151: an accessible name renders with JSON-style escaping (`- button "Save\"Now"`,
  `- button "back\\slash"`), which the wrap reproduces for neither. **Refuses rather
  than reproducing that escaping**, because mirroring a third-party rendering convention
  would rest the invariant on something this module cannot pin, and no corpus `text=`
  value carries either character (re-measured after the fix: still 47 change branch, 0
  non-text, 0 of the 47 refused). RED first: 2 failing cases, `actual '"Save"Now"'` vs
  `expected null`. Tests carry the byte-exact captured snapshot lines, so a future
  change that makes any of these non-null is grepped against real bytes.
- DONE: Record that the grammar authority's own primary form cannot be clicked.
  Probed live rather than reasoned: `is visible 'role=button[name="AlphaBtn"]'` and
  `is visible 'text=AlphaBtn'` both returned **false** against a fixture whose snapshot
  showed the button, while `[role="button"][aria-label="通知"]` and `h1` returned
  **true**. So forms 2 and 3 resolve on the translated visibility path only, and an
  element they locate that a step also clicks or fills needs `css_selector:`. This was
  **outside the approved scope** — the cycle-1 record deferred it as "worth a follow-up
  spike". Closed here instead of deferred because the probe contradicted what a mapper
  author would infer from the priority list, and leaving the single authority saying
  something a live probe refutes is the exact defect class this entity exists to remove.
  Flagged for the captain as a scope note, not presented as in-scope.
- DONE: Full suite at the exit. **891/892 passing**, 161 suites, 1 skipped (opt-in
  browser test). Scoped `selector-translate.test.js` 27/27.
- NOTE: One full-suite run surfaced an unrelated failure in
  `compiler/test/trace-finalization.test.js`. Not written off by impression: isolated to
  load-flakiness (49/49 standalone on this branch twice, 49/49 standalone on clean
  `main`, green on the full-suite re-run) and filed as **#122** rather than dismissed.

## Stage Report: validation

Fresh-context validator, two lenses, and a cross-vendor pass, all against exact head
`4fe0597`. The implementer's self-report was not accepted for any AC.

- **Lenses:** correctness (exercise-based, live browser) PASS · silent-failure — 1 MEDIUM
  finding, **confirmed a real defect and fixed** (see cycle 3 above), 1 correctly
  identified as pre-existing and out of scope · manifest/back-compat PASS. Not fired,
  with the touched surfaces named instead: no new or changed type, no lock / async
  ordering / shared mutable state, no process or handle lifecycle, no auth or trust
  boundary, no workflow file.
- **Diff coverage:** **100%** — 58/58 added executable lines instrumented and covered,
  bar 85%. The only added executable logic is in `selector-translate.js`;
  `lint-mapping.sh`'s additions are all `usage()` strings, the rest deletions and
  comments.
- **Adversarial:** 4 claim-breaking edits in scratch copies, all red as specified —
  remove the regex refusal (7/25), revert the chord strip (7/25), remove the new
  escaping refusal (2/27), restore lint CLASS 1 (corpus 2/5 → **5/5** failing, which is
  AC-1's own stated falsifier).
- **Cross-model:** codex (cross-vendor from a Claude session), run on exact head
  `4fe0597` after the two new commits — the earlier run against a pre-commit diff was
  discarded rather than recorded, so the gate reflects the bytes that merge.
- **E2E:** AC-3 exercised against a **live** agent-browser 0.32.0 + Chrome for Testing
  151 snapshot, driven through the plugin's own owned browser runtime (isolated
  namespace, Chrome for Testing pinned, closed after). 9 cases including a negative
  control (`text=NotPresent` must not hit) and the regex refusal, checked through both a
  real `grep -F` subprocess and the exact Bash substring test codegen emits.

### AC disposition

- **AC-1 → PARTIAL**, exactly as the cycle-1 re-score corrected it. Corpus 5/5 → 2/5
  failing; residue **exclusively** still-banned CLASS 2 (`>> nth=`, 39 occurrences).
  Nothing un-banned still fails. The validator reproduced the falsifier independently.
- **AC-2 → PASS.** Sweep for `silently mishandled` / `executed directly` clean outside
  `CHANGELOG.md` (release-please-owned, not hand-edited).
- **AC-3 → PASS**, exercised not read. The validator confirmed by reading the test
  source that the AC-3 group genuinely shells out to `grep -Fq`, and found **no
  decorative assertion** — no added behavior-claiming assertion that no RED run could
  reach.

### One reviewer claim rejected on evidence

The silent-failure lens argued the un-ban creates no new click/fill risk partly because
"agent-browser's Playwright-backed click/fill already parses these forms natively" and
because 2,183 occurrences over three months with no attributed failures showed the path
was exercised. **The live probe above refutes the premise** — agent-browser drives CDP,
is not Playwright, and returns `false` for both forms on that path. Its *conclusion* still
holds (the path is pre-existing, `codegen.js` is untouched), so the finding's disposition
is unchanged, but the reasoning was not adopted and the doc now records what was measured.

### Residuals, accepted rather than fixed

1. The same byte-fidelity class in the **pre-existing** `role=` branch for a backslash
   value. Outside approved scope; filed as **#121** together with the already-tracked
   [[e2e-regex-prefix-false-match]] instance, because one convention should close both.
2. The 39 `>> nth=` corpus occurrences stay grandfathered. Owner entity
   [[e2e-nth-chord-widening]] is still `backlog` with no issue and no sprint, so this
   deferral has **no landing date** — recorded plainly because "deferred to X" reads
   stronger than it is.
3. Wider-corpus magnitudes in this entity's earlier record (26/32, 19/32, the 295- and
   81-selector counts) are **not reproducible from this machine**. The reachable corpus
   is 5 mapping files / 310 unique selectors, so the falsifier direction is confirmed
   locally but not those exact figures.

## Measurement

Cycles 1 and 2 (2026-07-25) were never instrumented and their sessions are gone, so
their dispatch and token figures are **unrecoverable, not zero**. Cycle 3 is instrumented
below. Per the `+` convention the roll-up is therefore a floor, excluded from baseline
and bar comparisons.

- dispatch 1 — EM sprint-entry gate (`ship-flow:science-officer-em`, opus): ~100K
- dispatch 2 — cross-vendor design consult on the #91 contract (codex): ~158K
- dispatch 3 — fresh-context AC validator (sonnet): ~111K
- dispatch 4 — silent-failure lens (`pr-review-toolkit:silent-failure-hunter`, sonnet): ~82K
- dispatch 5 — cross-model gate on exact head (codex): recorded at return
- dispatch 6 — cross-model gate, first run, discarded as stale-diff: not counted toward
  evidence, counted here because it consumed a dispatch
- cycles 1-2 — unrecoverable

`dispatches = 6+` (cycle 3 only; cycles 1-2 unknown), `rework_rounds = 2`,
`diff_coverage = 100`, `tokens_if_known` is a floor.

**No `ledger.csv` row is written from this workspace.** It is a state non-holder, and the
`pr-merge` lifecycle hooks that replace the two pre-merge sentinels fail closed off the
registered holder, which a concurrent `kc-pr-flow` session owns. Writing a row whose
sentinels nothing here can finalize would leave an incomplete row that the terminal
verifier rejects — worse than none. Same boundary as #104 / #107 / #110, which also
carry no row. Bookkeeping is owed to the holder; the code is not blocked on it.
