package net.tomczek.ba.multi.model.mcp.test.application.interceptor;

import net.tomczek.ba.multi.model.mcp.test.application.service.InferenceApiLoggingService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class HttpLoggingInterceptor implements ClientHttpRequestInterceptor {

    private static final Logger HTTP_LOG = LoggerFactory.getLogger("HTTP_FILE");

    private final InferenceApiLoggingService inferenceApiLoggingService;

    @Autowired
    public HttpLoggingInterceptor(InferenceApiLoggingService inferenceApiLoggingService) {
        this.inferenceApiLoggingService = inferenceApiLoggingService;
    }

    @Override
    public ClientHttpResponse intercept(
            HttpRequest request,
            byte[] body,
            ClientHttpRequestExecution execution) throws IOException {

        logRequestHeaders(request, body);

        ClientHttpResponse response = execution.execute(request, body);

        logResponseHeaders(response);

        String model = extractModel(request, body);

        if (inferenceApiLoggingService != null) {
            inferenceApiLoggingService.logRateLimitInfo(model, response.getHeaders());
        }

        return response;
    }

    private void logRequestHeaders(HttpRequest request, byte[] body) {
        String requestHeaders = request.getHeaders().entrySet().stream()
                .map(entry -> {
                    String key = entry.getKey();
                    String value = String.join(",", entry.getValue());

                    if (isSensitiveHeader(key)) {
                        value = maskSensitiveValue(value);
                    }

                    return key + "=" + value;
                })
                .collect(Collectors.joining(" | "));

        HTTP_LOG.info("REQUEST | method={} | url={} | headers={} | body={}",
                request.getMethod(),
                normalizeForLog(request.getURI().toString()),
                normalizeForLog(requestHeaders),
                normalizeForLog(new String(body)));
    }

    private void logResponseHeaders(ClientHttpResponse response) throws IOException {
        String responseHeaders = response.getHeaders().entrySet().stream()
                .map(entry -> {
                    String key = entry.getKey();
                    String value = String.join(",", entry.getValue());

                    if (isSensitiveHeader(key)) {
                        value = maskSensitiveValue(value);
                    }

                    return key + "=" + value;
                })
                .collect(Collectors.joining(" | "));

        HTTP_LOG.info("RESPONSE | status={} | headers={}",
                response.getStatusCode(),
                normalizeForLog(responseHeaders));
    }

    private boolean isSensitiveHeader(String headerName) {
        if (headerName == null) {
            return false;
        }

        String lowerName = headerName.toLowerCase();
        return lowerName.contains("authorization") ||
               lowerName.contains("auth") ||
               lowerName.contains("key") ||
               lowerName.contains("secret");
    }

    private String maskSensitiveValue(String value) {
        if (value == null || value.length() <= 8) {
            return "****";
        }
        return value.substring(0, 4) + "****" + value.substring(value.length() - 4);
    }

    private String extractModel(HttpRequest request, byte[] body) {
        List<String> modelHeader = request.getHeaders().get("X-Model");
        if (modelHeader != null && !modelHeader.isEmpty()) {
            return modelHeader.get(0);
        }

        if (body != null && body.length > 0) {
            try {
                String bodyStr = new String(body);

                if (bodyStr.contains("\"model\"")) {
                    String[] parts = bodyStr.split("\"model\"\\s*:\\s*\"");
                    if (parts.length > 1) {
                        String modelPart = parts[1];
                        int endIndex = modelPart.indexOf("\"");
                        if (endIndex > 0) {
                            return modelPart.substring(0, endIndex);
                        }
                    }
                }
            } catch (Exception e) {
                // Ignore
            }
        }

        return "unknown";
    }

    /**
     * Entfernt Zeilenumbrüche für einzeilige Log-Einträge und kürzt sehr lange Strings
     */
    private String normalizeForLog(String s) {
        if (s == null) {
            return "";
        }
        return s.replaceAll("\\r\\n|\\r|\\n", "↵");
    }
}
