package net.tomczek.ba.multi.model.mcp.test.application.config;

import net.tomczek.ba.multi.model.mcp.test.application.service.McpLoggingService;
import org.springframework.ai.mcp.AsyncMcpToolCallbackProvider;
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.definition.ToolDefinition;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import java.util.Arrays;

@Configuration
public class McpLoggingConfiguration {

    @Bean
    @Primary
    public SyncMcpToolCallbackProvider loggingMcpToolCallbackProvider(
            SyncMcpToolCallbackProvider originalProvider,
            McpLoggingService mcpLoggingService) {

        return new SyncMcpToolCallbackProvider() {
            @Override
            public ToolCallback[] getToolCallbacks() {
                ToolCallback[] originalCallbacks = originalProvider.getToolCallbacks();

                return Arrays.stream(originalCallbacks)
                        .map(callback -> new LoggingToolCallback(callback, mcpLoggingService))
                        .toArray(ToolCallback[]::new);
            }
        };
    }

    private static class LoggingToolCallback implements ToolCallback {
        private final ToolCallback delegate;
        private final McpLoggingService mcpLoggingService;

        public LoggingToolCallback(ToolCallback delegate, McpLoggingService mcpLoggingService) {
            this.delegate = delegate;
            this.mcpLoggingService = mcpLoggingService;
        }

        @Override
        public String call(String input) {
            String toolName = delegate.getToolDefinition().name();

            mcpLoggingService.logIncomingMessage("TOOL_CALL_REQUEST",
                    String.format("Tool: %s, Input: %s", toolName, input));

            long startTime = System.currentTimeMillis();
            try {
                String result = delegate.call(input);

                long endTime = System.currentTimeMillis();
                long durationMs = endTime - startTime;

                mcpLoggingService.logToolCall(toolName, input, result);
                mcpLoggingService.logOutgoingMessage("TOOL_CALL_RESPONSE",
                        String.format("Tool: %s, Duration: %d ms, Result length: %s, Result: %s", toolName, durationMs, result.length(), result));

                return result;
            } catch (Exception e) {
                long endTime = System.currentTimeMillis();
                long durationMs = endTime - startTime;

                mcpLoggingService.logError("TOOL_CALL",
                        String.format("Fehler beim Aufruf von Tool: %s nach %d ms", toolName, durationMs), e);
                throw e;
            }
        }

        @Override
        public ToolDefinition getToolDefinition() {
            return delegate.getToolDefinition();
        }
    }
}
