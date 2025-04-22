import logging
from typing import Optional

logger = logging.getLogger("agentverse.wallet")

class AgentWallet:
    def __init__(self, agent_id: str, initial_balance: float = 0.0):
        self.agent_id = agent_id
        self.balance = initial_balance
        logger.info("[💸 WALLET] 🎧 'I left my wallet in El Segundo...' — Initializing token store for EVA '%s'", agent_id)

    def deposit(self, amount: float, reason: Optional[str] = None):
        self.balance += amount
        logger.info(
            "[💸 WALLET] 💵 'Back in the days on the boulevard of Linden...' — Deposited %.2f tokens to '%s'. Reason: %s",
            amount, self.agent_id, reason or "N/A"
        )

    def spend(self, amount: float, operation: str):
        logger.info("[💸 WALLET] 💬 'Can I kick it?' — Request to deduct %.2f tokens for operation: %s", amount, operation)
        if self.balance >= amount:
            self.balance -= amount
            logger.info("[💸 WALLET] ✅ 'Yes you can!' — Transaction approved for EVA '%s'. Balance: %.2f tokens", self.agent_id, self.balance)
            return True
        else:
            logger.warning("[💸 WALLET] 🚫 'Beats that knock, but this one broke the bank.' — Insufficient funds for EVA '%s'. Balance: %.2f, Required: %.2f", self.agent_id, self.balance, amount)
            return False

    def refund(self, amount: float, reason: Optional[str] = None):
        self.balance += amount
        logger.info("[💸 WALLET] 👉 'It’s the return of the funky wallet...' — Refunded %.2f tokens to '%s'. Reason: %s", amount, self.agent_id, reason or "N/A")

    def check_balance(self):
        logger.info("[💸 WALLET] 🧰 'You on point, Tip?' — 'All the time, Phife.' — Balance for EVA '%s': %.2f tokens", self.agent_id, self.balance)
        return self.balance

    def audit(self):
        logger.info("[💸 WALLET] 🧠 'Industry rule number 4080…' — Auditing wallet of EVA '%s'. Balance: %.2f tokens", self.agent_id, self.balance)
        return {
            "agent_id": self.agent_id,
            "balance": self.balance
        }