package net.tomczek.ba.multi.model.mcp.test.application;

import jakarta.annotation.PostConstruct;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.stereotype.Component;

import java.util.Arrays;

@Component
public class PrintTools {

    private final ToolCallbackProvider toolCallbackProvider;

    public PrintTools(ToolCallbackProvider toolCallbackProvider) {
        this.toolCallbackProvider = toolCallbackProvider;
    }

    @PostConstruct
    public void printTools() {
        System.out.println("Verfügbare Tools:");
        Arrays.stream(toolCallbackProvider.getToolCallbacks())
                .map(toolDef -> toolDef.getToolDefinition().name()).toList()
                .forEach(System.out::println);
    }
}
