package tests.utils;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Date;
import java.util.List;

public class CsvWriter {

    public static void writeToCSV(List<PromptResult> promptResults, String fileName) throws IOException {
        if (promptResults == null || promptResults.isEmpty()) {
            throw new IllegalArgumentException("PromptResults list cannot be null or empty");
        }

        File file = new File(fileName);

        boolean writeHeader = !file.exists();

        try (PrintWriter writer = new PrintWriter(new FileWriter(fileName, true))) {
            if (writeHeader) {
                writer.println("timestamp,model,runCount,prompt,tools,runtimeSumInMs,toolCallCount,mcpToolTokenSum,toolParameters,response,success");
            }

            for (PromptResult result : promptResults) {
                writer.println(formatPromptResultAsCSVRow(result));
            }
        }
    }

    private static String formatPromptResultAsCSVRow(PromptResult result) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd-HH-mm");

        return String.format("\"%s\",\"%s\",\"%d\",\"%s\",\"%s\",\"%.0f\",\"%d\",\"%d\",\"%s\",\"%s\",TBD",
                formatter.format(result.timestamp().toInstant().atZone(ZoneId.systemDefault())),
                escapeCSV(result.model()),
                result.runCount(),
                escapeCSV(result.prompt()),
                escapeCSV(formatListAsString(result.tools())),
                result.runtimeSumInMs(),
                result.toolCallCount(),
                result.mcpToolTokenSum(),
                escapeCSV(formatListAsString(result.toolParameters())),
                escapeCSV(result.response())
        );
    }

    private static String escapeCSV(String value) {
        if (value == null) {
            return "";
        }

        return value.replace("\"", "\"\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r");
    }

    private static String formatListAsString(List<String> list) {
        if (list == null || list.isEmpty()) {
            return "";
        }
        return String.join("|", list);
    }
}
