package tests.utils;

import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class Commons {
    public static final List<String> MODELS = List.of(
            "openai-gpt-4.1-mini",
            "mistral-ai-mistral-medium-2505"
    );

    public static final int TEST_COUNT = 2;

    public static List<PromptResult> run(String prompt, List<String> tools) {
        RestClient client = RestClient.builder().baseUrl("http://localhost:8100").build();
        List<PromptResult> runResults = new ArrayList<>();
            for (String model : MODELS) {
                for (int i = 0; i < TEST_COUNT; i++) {
                    try {
                        String response = client.post()
                                .uri(uriBuilder -> {
                                    uriBuilder.path("/api/chat/" + model);
                                    tools.forEach(tool -> uriBuilder.queryParam("enabledTools", tool));
                                    return uriBuilder.build();
                                })
                                .contentType(MediaType.APPLICATION_JSON)
                                .body(prompt)
                                .retrieve().body(String.class);
                        AnalysisResult analysisResult = LogAnalyzer.analyzeMcpLog("logs/mcp.log");
                        runResults.add(new PromptResult(new Date(), model, i, prompt, tools, analysisResult.timingSum(), analysisResult.incomingCount(), analysisResult.resultLengthSum(), analysisResult.inputParameters(), response));
                        System.out.println("Completed run for model " + model + " iteration " + i + ".");
                        System.out.println("Asnwer: " + response);
                        LogAnalyzer.clearLog("logs/mcp.log");
                        System.out.println("----- Waiting 20 seconds before next run. -----");
                        Thread.sleep(20000);

                    } catch (InterruptedException ignored) {

                    } catch (Exception e) {
                        runResults.add(new PromptResult(new Date(), model, i, prompt, tools, -1, -1, -1, List.of(), e.getMessage()));
                    }
                }
            }
        return runResults;
    }
}
