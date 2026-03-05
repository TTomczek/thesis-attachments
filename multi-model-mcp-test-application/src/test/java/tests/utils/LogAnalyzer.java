package tests.utils;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class LogAnalyzer {

    public static void clearLog(String logPath) throws IOException {
        Path path = Paths.get(logPath);
        Files.write(path, new byte[0], StandardOpenOption.TRUNCATE_EXISTING, StandardOpenOption.WRITE);
        System.out.println("Cleared log file at: " + logPath);
    }

    public static AnalysisResult analyzeMcpLog(String logPath) {
        Path path = Paths.get(logPath);

        if (!Files.exists(path)) {
            return new AnalysisResult(path.getFileName().toString(), 0, 0.0f, 0, 0, new ArrayList<>());
        }

        int incomingCount = 0;
        double timingSum = 0.0;
        int resultLengthSum = 0;
        int processedLines = 0;
        List<String> inputParameters = new ArrayList<>();

        Pattern incomingPattern = Pattern.compile("INCOMING \\| ");
        Pattern timingPattern = Pattern.compile("(\\d+(?:\\.\\d+)?)\\s+ms");
        Pattern resultLengthPattern = Pattern.compile("Result length:\\s+(\\d+)");
        Pattern toolInputPattern = Pattern.compile("Tool:\\s*([^,]+),\\s*Input:\\s*(\\{.*})");

        ObjectMapper objectMapper = new ObjectMapper();

        try {
            List<String> lines = Files.readAllLines(path);

            for (String line : lines) {
                processedLines++;

                if (incomingPattern.matcher(line).find()) {
                    incomingCount++;
                }

                Matcher timingMatcher = timingPattern.matcher(line);
                if (timingMatcher.find()) {
                    double timingValue = Double.parseDouble(timingMatcher.group(1));
                    timingSum += timingValue;
                }

                Matcher resultLengthMatcher = resultLengthPattern.matcher(line);
                if (resultLengthMatcher.find()) {
                    int resultLength = Integer.parseInt(resultLengthMatcher.group(1));
                    resultLengthSum += resultLength;
                }

                String inputParams = extractInputParameters(line, toolInputPattern, objectMapper);
                if (inputParams != null) {
                    inputParameters.add(inputParams);
                }
            }

        } catch (IOException e) {
            return new AnalysisResult(path.getFileName().toString(), 0, 0.0f, 0, 0, new ArrayList<>());
        }

        return new AnalysisResult(path.getFileName().toString(), incomingCount, timingSum,
                                  resultLengthSum, processedLines, inputParameters);
    }

    private static String extractInputParameters(String logLine, Pattern toolInputPattern, ObjectMapper objectMapper) {
        Matcher matcher = toolInputPattern.matcher(logLine);

        if (matcher.find()) {
            String toolName = matcher.group(1).trim();
            String jsonInput = matcher.group(2);

            try {
                JsonNode inputObject = objectMapper.readTree(jsonInput);

                List<String> nameValuePairs = new ArrayList<>();
                nameValuePairs.add("Tool: " + toolName);

                formatJsonNode(inputObject, "", nameValuePairs);

                return String.join("; ", nameValuePairs);

            } catch (JsonProcessingException e) {
                return null;
            }
        }

        return null;
    }

    private static void formatJsonNode(JsonNode node, String prefix, List<String> nameValuePairs) {
        if (node.isObject()) {

            node.fields().forEachRemaining(entry -> {
                String fullName = prefix.isEmpty() ? entry.getKey() : prefix + "." + entry.getKey();
                formatJsonNode(entry.getValue(), fullName, nameValuePairs);
            });
        } else if (node.isArray()) {

            List<String> arrayValues = new ArrayList<>();

            node.elements().forEachRemaining(element -> {
                if (element.isValueNode()) {
                    arrayValues.add(element.asText());
                } else {
                    arrayValues.add(element.toString());
                }
            });

            nameValuePairs.add(prefix + ": [" + String.join(", ", arrayValues) + "]");
        } else {
            nameValuePairs.add(prefix + ": " + node.asText());
        }
    }
}
