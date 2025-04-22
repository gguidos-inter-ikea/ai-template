from src.domains.agentverse.logging.logger import log_command_room as system_logger


class CommandRoomTransmitter:
    def __init__(self, commbridge):
        """
        Transmitter for system-wide or targeted logs that flow to the AgentVerse.
        """
        self.commbridge = commbridge

    async def to_agent(self, agent_name: str, message: str):
        """
        Sends a Command Room log to a specific agent channel.
        """
        channel = f"agent:{agent_name.lower()}"
        system_logger(f"[🧠 Command Room → {agent_name}] {message}")
        await self.commbridge.redis_repository.publish(channel, f"[💠 Command Room] {message}")

    async def to_socket(self, socket_id: str, message: str):
        """
        Sends a Command Room message directly to a socket.
        """
        system_logger(f"[🧠 Command Room → socket:{socket_id}] {message}")
        await self.commbridge.send_to_socket(socket_id, f"[💠 Command Room] {message}")

    async def broadcast(self, message: str):
        """
        Broadcasts a message to all active sockets.
        """
        system_logger(f"[🧠 Command Room → ALL] {message}")
        await self.commbridge.broadcast_to_all(f"[💠 Command Room] {message}")
