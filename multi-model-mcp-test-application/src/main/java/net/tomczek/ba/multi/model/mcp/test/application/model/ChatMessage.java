package net.tomczek.ba.multi.model.mcp.test.application.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.LocalDateTime;

public class ChatMessage {
    private final String role; // "user" oder "assistant"
    private final String content;
    private final LocalDateTime timestamp;

    @JsonCreator
    public ChatMessage(@JsonProperty("role") String role,
                      @JsonProperty("content") String content,
                      @JsonProperty("timestamp") LocalDateTime timestamp) {
        this.role = role;
        this.content = content;
        this.timestamp = timestamp != null ? timestamp : LocalDateTime.now();
    }

    public ChatMessage(String role, String content) {
        this(role, content, LocalDateTime.now());
    }

    public String getRole() {
        return role;
    }

    public String getContent() {
        return content;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    @Override
    public String toString() {
        return "ChatMessage{" +
                "role='" + role + '\'' +
                ", content='" + content + '\'' +
                ", timestamp=" + timestamp +
                '}';
    }
}
