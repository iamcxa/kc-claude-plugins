---
title: Diagnosis rounds on one symptom count toward the step back
status: backlog
variant: kc-dev-flow-2
---

Repeated diagnosis rounds on the same symptom inside one stage reach the step-back questions, the way a second failed validation or a second replacing amendment already does.

Source: the Captain, chat 2026-11-03: 「ABC 都開，不屬於套件的本身也要討論一下」, answering 「決定：A、B、C 三個都開成 dev2 任務，跟 #768 一起發版嗎？要刪哪個直接說。」 He also said 「先不合併，我想要把這些也評估修復後，再一起發版」 about Release PR #768. FO had proposed it as: 「診斷回合要按『同一個症狀』累計」.

Gap: the step-back reminder from PR #766 counts failed validations and replacing amendments only; rounds inside one validation do not count.

Bite: the agent-observatory report on the qnow FO, 2026-11-03 (sampled, not yet checked against the source by FO). One mobile-width freeze was chased through more than six browser runs from 2026-10-30 17:58 to 21:05, and stopped only when the Captain tried it by hand and it did not reproduce.

Consumer: every adopter FO and its validation workers, through the reminder that role_triggers.py already prints.
