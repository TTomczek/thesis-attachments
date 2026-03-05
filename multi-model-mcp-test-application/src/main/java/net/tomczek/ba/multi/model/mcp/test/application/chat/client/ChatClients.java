package net.tomczek.ba.multi.model.mcp.test.application.chat.client;

import net.tomczek.ba.multi.model.mcp.test.application.interceptor.HttpLoggingInterceptor;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

@Configuration
public class ChatClients {

    @Value("${GITHUB_API_KEY:}")
    private String githubApiKey;

    @Value("${spring.ai.github.base-url:}")
    private String githubBaseUrl;

    private final HttpLoggingInterceptor httpLoggingInterceptor;

    @Autowired
    public ChatClients(HttpLoggingInterceptor httpLoggingInterceptor) {
        this.httpLoggingInterceptor = httpLoggingInterceptor;
    }

    public ChatClient gpt41miniChatClientGH(ToolCallbackProvider toolCallbackProvider) {
        var openAiApi = OpenAiApi.builder()
                .apiKey(githubApiKey)
                .baseUrl(githubBaseUrl)
                .restClientBuilder(createRestClientWithInterceptor())
                .build();
        var openAiChatOptions = OpenAiChatOptions.builder()
                .model("openai/gpt-4.1-mini")
                .build();
        var openAiChatModel = OpenAiChatModel.builder()
                .openAiApi(openAiApi)
                .defaultOptions(openAiChatOptions)
                .build();
        return ChatClient
                .builder(openAiChatModel)
                .build();
    }

    @Bean
    public MMMTAChatClient mmmtaChatClientGpt41mini(ToolCallbackProvider toolCallbackProvider) {
        return new MMMTAChatClient(
                "GitHub GPT-4.1-Mini",
                "openai/gpt-4.1-mini",
                gpt41miniChatClientGH(toolCallbackProvider)
        );
    }

    public ChatClient mistralmedium2505ChatClientGH(ToolCallbackProvider toolCallbackProvider) {
        var openAiApi = OpenAiApi.builder()
                .apiKey(githubApiKey)
                .baseUrl(githubBaseUrl)
                .restClientBuilder(createRestClientWithInterceptor())
                .build();
        var openAiChatOptions = OpenAiChatOptions.builder()
                .model("mistral-ai/mistral-medium-2505")
                .build();
        var openAiChatModel = OpenAiChatModel.builder()
                .openAiApi(openAiApi)
                .defaultOptions(openAiChatOptions)
                .build();
        return ChatClient
                .builder(openAiChatModel)
                .build();
    }

    @Bean
    public MMMTAChatClient mmmtaChatClientMistralMedium2505(ToolCallbackProvider toolCallbackProvider) {
        return new MMMTAChatClient(
                "GitHub Mistral Medium 2505",
                "mistral-ai/mistral-medium-2505",
                mistralmedium2505ChatClientGH(toolCallbackProvider)
        );
    }

    /**
     * Erstellt eine RestTemplate-Instanz mit HTTP-Logging-Interceptor
     */
    private RestClient.Builder createRestClientWithInterceptor() {
        RestTemplate restTemplate = new RestTemplate();
        List<ClientHttpRequestInterceptor> interceptors = new ArrayList<>();
        interceptors.add(httpLoggingInterceptor);
        restTemplate.setInterceptors(interceptors);
        return RestClient.builder(restTemplate);
    }
}
