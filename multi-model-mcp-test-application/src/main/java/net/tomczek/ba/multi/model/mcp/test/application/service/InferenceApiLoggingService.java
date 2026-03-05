package net.tomczek.ba.multi.model.mcp.test.application.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class InferenceApiLoggingService {

    private static final Logger INFERENCE_LOG = LoggerFactory.getLogger("HTTP_FILE");

    /**
     * Loggt Rate-Limiting-Informationen
     */
    public void logRateLimitInfo(String model, HttpHeaders responseHeaders) {
        if (responseHeaders == null) return;

        StringBuilder logEntry = new StringBuilder();
        logEntry.append("INFERENCE_API_CALL | model=").append(model);

        addHeaderToLog(logEntry, "gh_limit_requests", responseHeaders.get("x-ratelimit-limit-requests"));
        addHeaderToLog(logEntry, "gh_limit_tokens", responseHeaders.get("x-ratelimit-limit-tokens"));
        addHeaderToLog(logEntry, "prompt_token_len", responseHeaders.get("prompt_token_len"));
        addHeaderToLog(logEntry, "gh_remaining_requests", responseHeaders.get("x-ratelimit-remaining-requests"));
        addHeaderToLog(logEntry, "gh_remaining_tokens", responseHeaders.get("x-ratelimit-remaining-tokens"));
        addHeaderToLog(logEntry, "request_time", responseHeaders.get("x-request-time"));

        INFERENCE_LOG.info(logEntry.toString());
    }

    /**
     * Hilfsmethode zum Hinzufügen von Headern zum Log-Eintrag
     */
    private void addHeaderToLog(StringBuilder logEntry, String name, Object value) {
        if (value != null) {
            String valueStr;
            if (value instanceof List) {
                valueStr = ((List<?>) value).stream()
                        .map(Object::toString)
                        .collect(Collectors.joining(","));
            } else {
                valueStr = value.toString();
            }

            if (!valueStr.isEmpty()) {
                logEntry.append(" | ").append(name).append("=").append(normalizeForLog(valueStr));
            }
        }
    }

    private String normalizeForLog(String logMessage) {
        if (logMessage == null) {
            return "";
        }

        return logMessage.replaceAll("\\r\\n|\\r|\\n", "↵");
    }
}
