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

public class CustomEveIT extends BaseIT {

    static Stream<Arguments> testScenariosProvider() {
        return Stream.of(
            Arguments.of(
                1, "Get the number of all available ships. Answer only with the number. Ships have item category 6.",
                List.of("get_type_ids_of_category")
            ),
            Arguments.of(
                2, "Get the amount of structure points of the ship 'star destroyer'. Answer only with the number.", List.of("get_ship_infos"))
        );
    }

    @ParameterizedTest
    @MethodSource("testScenariosProvider")
    public void testScenarios(int scenarioNumber, String prompt, List<String> tools) throws IOException {
        List<PromptResult> promptResults = Commons.run(prompt, tools);
        CsvWriter.writeToCSV(promptResults, String.format("manuell_stage_%s_eve.csv", OPTIMIZATION_STAGE));
    }
}
