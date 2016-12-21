<?php

use Behat\Behat\Context\ClosuredContextInterface,
    Behat\Behat\Context\TranslatedContextInterface,
    Behat\Behat\Context\BehatContext,
    Behat\Behat\Exception\PendingException;
use Behat\Gherkin\Node\PyStringNode,
    Behat\Gherkin\Node\TableNode;

//
// Require 3rd-party libraries here:
//
//   require_once 'PHPUnit/Autoload.php';
//   require_once 'PHPUnit/Framework/Assert/Functions.php';
//

/**
 * Features context.
 */
class FeatureContext extends BehatContext
{
    /**
     * Initializes context.
     * Every scenario gets its own context object.
     *
     * @param array $parameters context parameters (set them up through behat.yml)
     */
    public function __construct(array $parameters)
    {
        // Initialize your context here
    }

    /**
     * @Given /^the current project,$/
     */
    public function theCurrentProject()
    {
        $projDir = dirname(dirname(dirname(__FILE__)));
        if (getcwd() != $projDir) {
            chdir($projDir);
        }
    }

    /**
     * @Given /^a file "([^"]*)" containing:$/
     */
    public function aFileContaining($fileName, PyStringNode $contents)
    {
        file_put_contents($fileName, (string) $contents);
    }

    /**
     * @When /^the user runs:$/
     */
    public function theUserRuns(PyStringNode $command)
    {
        exec((string) $command, $output, $return_var);
        if ($return_var) {
            throw new Exception("Command return non-zero: '$return_var' for '$command'");
        }
        $this->output = trim(implode("\n", $output));
    }

    /**
     * @Then /^file "([^"]*)" should be created, and contain the same as "([^"]*)"$/
     */
    public function fileShouldBeCreatedAndContainTheSameAs($outputFileName, $expectedContentsFileName)
    {
        if (!file_exists($outputFileName)) {
            throw new Exception("File '$outputFileName' does not exist");
        }

        if (file_get_contents($outputFileName) !=
                file_get_contents($expectedContentsFileName)) {
            throw new Exception("File '$outputFileName' contents do not match '$expectedContentsFileName'");
        }
    }
}
