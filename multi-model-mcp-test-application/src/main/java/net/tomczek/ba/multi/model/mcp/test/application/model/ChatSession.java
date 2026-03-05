package net.tomczek.ba.multi.model.mcp.test.application.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class ChatSession {
    private final String sessionId;
    private final String title;
    private final LocalDateTime createdAt;
    private final List<ChatMessage> messages;
    private LocalDateTime lastActivity;

    @JsonCreator
    public ChatSession(@JsonProperty("sessionId") String sessionId,
                      @JsonProperty("title") String title,
                      @JsonProperty("createdAt") LocalDateTime createdAt,
                      @JsonProperty("messages") List<ChatMessage> messages,
                      @JsonProperty("lastActivity") LocalDateTime lastActivity) {
        this.sessionId = sessionId != null ? sessionId : UUID.randomUUID().toString();
        this.title = title != null ? title : "Neue Konversation";
        this.createdAt = createdAt != null ? createdAt : LocalDateTime.now();
        this.messages = messages != null ? messages : new ArrayList<>();
        this.lastActivity = lastActivity != null ? lastActivity : LocalDateTime.now();
    }

    public ChatSession(String title) {
        this(null, title, null, null, null);
    }

    public void addMessage(ChatMessage message) {
        messages.add(message);
        lastActivity = LocalDateTime.now();
    }

    public String getSessionId() {
        return sessionId;
    }

    public String getTitle() {
        return title;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public List<ChatMessage> getMessages() {
        return messages;
    }

    public LocalDateTime getLastActivity() {
        return lastActivity;
    }

    public void updateLastActivity() {
        this.lastActivity = LocalDateTime.now();
    }

    @Override
    public String toString() {
        return "ChatSession{" +
                "sessionId='" + sessionId + '\'' +
                ", title='" + title + '\'' +
                ", createdAt=" + createdAt +
                ", messagesCount=" + messages.size() +
                ", lastActivity=" + lastActivity +
                '}';
    }
}
