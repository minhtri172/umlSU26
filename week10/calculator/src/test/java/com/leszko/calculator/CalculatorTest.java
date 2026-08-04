package com.leszko.calculator;
import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class CalculatorTest {
     private Calculator calculator = new Calculator();

     @Test
     public void testPositive() {
          assertEquals(2, calculator.sum(1, 1));
     }

     public void testZero() {
          assertEquals(0, calculator.sum(3, -3));
     }

     public void testNegative() {
          assertEquals(-1, calculator.sum(2, -3));
     }
}
