package net.tomczek.ba.multi.model.mcp.test.application.service;

import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

@Service
public class McpLoggingService {

    private static final Logger MCP_FILE = LoggerFactory.getLogger("MCP_FILE");
    private final ObjectMapper objectMapper;

    public McpLoggingService() {
        this.objectMapper = new ObjectMapper();
        // Konfiguration für Java 8 Zeit-Typen
        objectMapper.registerModule(new JavaTimeModule());
        objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        // Verhindere Fehler bei leeren Beans
        objectMapper.disable(SerializationFeature.FAIL_ON_EMPTY_BEANS);
    }

    /**
     * Loggt eingehende MCP-Nachrichten vom Server
     */
    public void logIncomingMessage(String messageType, Object message) {
        try {
            String jsonMessage;
            if (message instanceof String) {
                jsonMessage = (String) message;
            } else {
                jsonMessage = objectMapper.writeValueAsString(message);
            }
            MCP_FILE.info("INCOMING | type={} | message='{}'", messageType, normalizeForLog(jsonMessage));
        } catch (JsonProcessingException e) {
            // Fallback: Logge nur die toString()-Repräsentation ohne Stacktrace
            MCP_FILE.info("INCOMING | type={} | message='{}' | note=serialization_fallback",
                         messageType, normalizeForLog(String.valueOf(message)));
        }
    }

    /**
     * Loggt ausgehende MCP-Nachrichten zum Server
     */
    public void logOutgoingMessage(String messageType, Object message) {
        try {
            String jsonMessage = objectMapper.writeValueAsString(message);
            MCP_FILE.info("OUTGOING | type={} | message={}", messageType, normalizeForLog(jsonMessage));
        } catch (JsonProcessingException e) {
            MCP_FILE.warn("Fehler beim Serialisieren der ausgehenden MCP-Nachricht: {}", message, e);
        }
    }

    /**
     * Loggt MCP-Tool-Aufrufe
     */
    public void logToolCall(String toolName, Object parameters, Object result) {
        try {
            String paramJson = objectMapper.writeValueAsString(parameters);
            String resultJson = objectMapper.writeValueAsString(result);
            MCP_FILE.info("TOOL_CALL | name={} | parameters='{}' | result='{}'",
                         toolName, normalizeForLog(paramJson), normalizeForLog(resultJson));
        } catch (JsonProcessingException e) {
            MCP_FILE.info("TOOL_CALL | name={} | parameters='{}' | result='{}' | note=serialization_fallback",
                         toolName, normalizeForLog(String.valueOf(parameters)), normalizeForLog(String.valueOf(result)));
        }
    }

    /**
     * Loggt MCP-Fehler
     */
    public void logError(String operation, String error, Throwable throwable) {
        MCP_FILE.error("ERROR | operation={} | error={}", operation, normalizeForLog(error), throwable);
    }

    /**
     * Entfernt Zeilenumbrüche für einzeilige Log-Einträge
     */
    private String normalizeForLog(String s) {
        if (s == null) return "";
        return s.replaceAll("\\r\\n|\\r|\\n", "↵");
    }
}
