package net.tomczek.ba.multi.model.mcp.test.application.config;

import io.modelcontextprotocol.client.transport.customizer.McpSyncHttpClientRequestCustomizer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class McpClientBuilerCustomizing {

    @Value("${GITHUB_PAT:NOT_CONFIGURED}")
    private String GITHUB_PAT;

//    @Bean
//    public McpSyncHttpClientRequestCustomizer mcpSyncClientBuilderCustomizer() {
//        return (builder, method, endpoint, body,context) -> builder.header("Authorization", "Bearer " + GITHUB_PAT);
//        return (builder, method, endpoint, body, context) -> builder.header("Authorization", "Bearer 111");
//    }
}
