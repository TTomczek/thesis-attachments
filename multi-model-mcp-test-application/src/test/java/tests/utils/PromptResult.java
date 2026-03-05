package tests.utils;

import java.util.Date;
import java.util.List;

public record PromptResult(Date timestamp, String model, int runCount, String prompt, List<String> tools, double runtimeSumInMs,
                           int toolCallCount, int mcpToolTokenSum, List<String> toolParameters, String response) {
}
