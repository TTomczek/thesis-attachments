package net.tomczek.ba.multi.model.mcp.test.application.service;

import net.tomczek.ba.multi.model.mcp.test.application.chat.client.MMMTAChatClient;
import net.tomczek.ba.multi.model.mcp.test.application.model.ChatMessage;
import net.tomczek.ba.multi.model.mcp.test.application.model.ChatSession;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ChatService {

    private static final Logger CHAT_FILE = LoggerFactory.getLogger("CHAT_FILE");

    private final List<MMMTAChatClient> mmmtaChatClients;
    private final ChatSessionService chatSessionService;
    private final ToolCallbackProvider toolCallbackProvider;

    public ChatService(List<MMMTAChatClient> chatClients,
                       ChatSessionService chatSessionService,
                       ToolCallbackProvider toolCallbackProvider
    ) {
        this.mmmtaChatClients = chatClients;
        this.chatSessionService = chatSessionService;
        this.toolCallbackProvider = toolCallbackProvider;
    }

    public String chat(String provider, String prompt) {
        return chat(provider, prompt, null);
    }

    public String chat(String provider, String prompt, List<String> enabledTools) {
        String response;
        for (MMMTAChatClient client : mmmtaChatClients) {
            if (client.getName().replaceAll("/", "-").equals(provider)) {
                response = call(client.getChatClient(), prompt, enabledTools);
                CHAT_FILE.info("provider={} | prompt={} | response={} | enabledTools={} | note=Siehe logs/http.log",
                        provider, normalizeForLog(prompt), normalizeForLog(response), enabledTools);
                return response;
            }
        }
        throw new RuntimeException("No such chat client " + provider);
    }

    public String chatWithSession(String provider, String sessionId, String prompt, List<String> enabledTools) {
        for (MMMTAChatClient client : mmmtaChatClients) {
            if (client.getName().replaceAll("/", "-").equals(provider)) {
                ChatSession session = chatSessionService.getSession(sessionId)
                .orElseThrow(() -> new IllegalArgumentException("Session nicht gefunden: " + sessionId));

                // Benutzer-Nachricht zur Session hinzufügen
                ChatMessage userMessage = new ChatMessage("user", prompt);
                session.addMessage(userMessage);

                String response = callWithContext(client.getChatClient(), session.getMessages(), enabledTools);

                // Assistant-Antwort zur Session hinzufügen
                ChatMessage assistantMessage = new ChatMessage("assistant", response);
                session.addMessage(assistantMessage);

                CHAT_FILE.info("sessionId={} | provider={} | prompt={} | response={} | enabledTools={} | note=Siehe logs/http.log",
                        sessionId, provider, normalizeForLog(prompt), normalizeForLog(response), enabledTools);
                return response;
            }
        }
        throw new RuntimeException("No such chat client " + provider);
    }

    public String call(ChatClient model, String prompt) {
        return call(model, prompt, null);
    }

    public String call(ChatClient model, String prompt, List<String> enabledTools) {
        var promptBuilder = model.prompt().user(prompt);

        if (enabledTools != null && !enabledTools.isEmpty()) {
            ToolCallback[] filteredTools = getFilteredTools(enabledTools);
            promptBuilder = promptBuilder.toolCallbacks(filteredTools);
        }

        return promptBuilder.call().content();
    }

    public String callWithContext(ChatClient model, List<ChatMessage> messageHistory, List<String> enabledTools) {
        List<Message> messages = new ArrayList<>();

        for (ChatMessage chatMessage : messageHistory) {
            switch (chatMessage.getRole()) {
                case "user" -> messages.add(new UserMessage(chatMessage.getContent()));
                case "assistant" -> messages.add(new AssistantMessage(chatMessage.getContent()));
            }
        }

        var promptBuilder = model.prompt().messages(messages);

        if (enabledTools != null && !enabledTools.isEmpty()) {
            ToolCallback[] filteredTools = getFilteredTools(enabledTools);
            promptBuilder = promptBuilder.toolCallbacks(filteredTools);
        }

        return promptBuilder.call().content();
    }

    private ToolCallback[] getFilteredTools(List<String> enabledToolNames) {
        if (enabledToolNames == null || enabledToolNames.isEmpty()) {
            return new ToolCallback[0];
        }

        return Arrays.stream(toolCallbackProvider.getToolCallbacks())
                .filter(tool -> enabledToolNames.contains(tool.getToolDefinition().name()))
                .toArray(ToolCallback[]::new);
    }

    public Map<String, String> getAvailableProviders() {
        Map<String, String> providers = new HashMap<>();
        for (MMMTAChatClient client : mmmtaChatClients) {
            providers.put(client.getName(), client.getLabel());
        }
        return providers;
    }

    private String normalizeForLog(String logMessage) {
        if (logMessage == null) {
            return "";
        }

        return logMessage.replaceAll("\\r\\n|\\r|\\n", "↵");
    }
}
