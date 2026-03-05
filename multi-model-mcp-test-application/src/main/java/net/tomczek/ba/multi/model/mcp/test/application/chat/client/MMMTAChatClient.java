package net.tomczek.ba.multi.model.mcp.test.application.chat.client;

import org.springframework.ai.chat.client.ChatClient;

public class MMMTAChatClient {
    private String label;
    private String name;
    private ChatClient chatClient;

    public MMMTAChatClient(String label, String name, ChatClient chatClient) {
        this.label = label;
        this.name = name;
        this.chatClient = chatClient;
    }

    public String getLabel() {
        return label;
    }

    public MMMTAChatClient setLabel(String label) {
        this.label = label;
        return this;
    }

    public String getName() {
        return name;
    }

    public MMMTAChatClient setName(String name) {
        this.name = name;
        return this;
    }

    public ChatClient getChatClient() {
        return chatClient;
    }

    public MMMTAChatClient setChatClient(ChatClient chatClient) {
        this.chatClient = chatClient;
        return this;
    }
}
