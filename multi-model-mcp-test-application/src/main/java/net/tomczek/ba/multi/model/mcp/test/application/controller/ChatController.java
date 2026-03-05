package net.tomczek.ba.multi.model.mcp.test.application.controller;

import net.tomczek.ba.multi.model.mcp.test.application.model.ChatSession;
import net.tomczek.ba.multi.model.mcp.test.application.service.ChatService;
import net.tomczek.ba.multi.model.mcp.test.application.service.ChatSessionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;
    private final ChatSessionService chatSessionService;

    public ChatController(ChatService chatService, ChatSessionService chatSessionService) {
        this.chatService = chatService;
        this.chatSessionService = chatSessionService;
    }

    @PostMapping("/{provider}")
    public ResponseEntity<String> chat(@PathVariable String provider,
                                      @RequestBody String prompt,
                                      @RequestParam(required = false) List<String> enabledTools) {
        return ResponseEntity.ok(chatService.chat(provider, prompt, enabledTools));
    }

    @PostMapping("/{provider}/session/{sessionId}")
    public ResponseEntity<String> chatWithSession(@PathVariable String provider,
                                                 @PathVariable String sessionId,
                                                 @RequestBody String prompt,
                                                 @RequestParam(required = false) List<String> enabledTools) {
        return ResponseEntity.ok(chatService.chatWithSession(provider, sessionId, prompt, enabledTools));
    }

    @PostMapping("/sessions")
    public ResponseEntity<ChatSession> createSession(@RequestBody(required = false) String title) {
        String sessionTitle = (title != null && !title.trim().isEmpty()) ? title.trim() : "Neue Konversation";
        ChatSession session = chatSessionService.createSession(sessionTitle);
        return ResponseEntity.ok(session);
    }

    @GetMapping("/sessions")
    public ResponseEntity<List<ChatSession>> getSessions() {
        return ResponseEntity.ok(chatSessionService.getAllSessions());
    }

    @GetMapping("/sessions/{sessionId}")
    public ResponseEntity<ChatSession> getSession(@PathVariable String sessionId) {
        return chatSessionService.getSession(sessionId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/sessions/{sessionId}")
    public ResponseEntity<Void> deleteSession(@PathVariable String sessionId) {
        chatSessionService.deleteSession(sessionId);
        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/sessions")
    public ResponseEntity<Void> clearSessions() {
        chatSessionService.clearAllSessions();
        return ResponseEntity.ok().build();
    }

    @GetMapping("/providers")
    public ResponseEntity<Map<String, String>> getProviders() {
        return ResponseEntity.ok(chatService.getAvailableProviders());
    }
}

