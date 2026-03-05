package tests.manuell.custom;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import tests.utils.BaseIT;
import tests.utils.Commons;
import tests.utils.CsvWriter;
import tests.utils.PromptResult;

import java.io.IOException;
import java.util.List;
import java.util.stream.Stream;

public class CustomInvManIT extends BaseIT {

    static Stream<Arguments> testScenariosProvider() {
        return Stream.of(
                Arguments.of(
                        1,
                        "How many invoices are in the system? Answer only with the number.",
                        List.of("get_invoices")
                ),
                Arguments.of(
                        2,
                        "How many paid invoices are in the system? Answer only with the number.",
                        List.of("get_invoices")
                ),
                Arguments.of(
                        3,
                        "How many invoices does the customer Musterfirma has? Answer only with the number",
                        List.of("get_invoices")
                ),
                Arguments.of(
                        4,
                        "Create an Invoice with one position of 'Materials' with 100 Pieces and 10$ per piece. The customer is Musterfirma. The service is provided from today. Use default values for other required missing fields. Answer with the id of the created invoice",
                        List.of("create_invoice")
                ),
                Arguments.of(
                        5,
                        "Create and download the invoice for the latest invoice of customer Musterfirma",
                        List.of("get_invoices", "download_invoice")
                )
        );
    }

    @ParameterizedTest
    @MethodSource("testScenariosProvider")
    public void testScenarios(int scenarioNumber, String prompt, List<String> tools) throws IOException {
        List<PromptResult> promptResults = Commons.run(prompt, tools);
        CsvWriter.writeToCSV(promptResults, String.format("manuell_stage_%s_invoice-manager.csv", OPTIMIZATION_STAGE));
    }
}
