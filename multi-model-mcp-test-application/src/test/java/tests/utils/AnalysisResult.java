package tests.utils;

import java.util.List;

public record AnalysisResult(String fileName, int incomingCount, double timingSum, int resultLengthSum,
                             int processedLines, List<String> inputParameters) { }
