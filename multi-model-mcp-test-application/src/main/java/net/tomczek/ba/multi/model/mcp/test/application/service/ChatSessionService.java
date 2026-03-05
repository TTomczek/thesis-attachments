package net.tomczek.ba.multi.model.mcp.test.application.service;

import net.tomczek.ba.multi.model.mcp.test.application.model.ChatMessage;
import net.tomczek.ba.multi.model.mcp.test.application.model.ChatSession;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class ChatSessionService {

    private final Map<String, ChatSession> sessions = new ConcurrentHashMap<>();

    public ChatSession createSession(String title) {
        ChatSession session = new ChatSession(title);
        sessions.put(session.getSessionId(), session);
        return session;
    }

    public Optional<ChatSession> getSession(String sessionId) {
        return Optional.ofNullable(sessions.get(sessionId));
    }

    public List<ChatSession> getAllSessions() {
        return new ArrayList<>(sessions.values());
    }

    public void deleteSession(String sessionId) {
        sessions.remove(sessionId);
    }

    public void clearAllSessions() {
        sessions.clear();
    }
}
