import React, { useState } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Check, X, Loader2, UserCircle, Users } from 'lucide-react';

const PersonaFeedback = ({ feedback, persona, onAccept, onReject }) => {
  return (
    <Card className="mb-4">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          <div className="flex items-center gap-2">
            <UserCircle className="h-4 w-4" />
            {persona}
          </div>
        </CardTitle>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="icon" 
            className="h-8 w-8" 
            onClick={() => onAccept(persona, feedback)}
          >
            <Check className="h-4 w-4" />
          </Button>
          <Button 
            variant="outline" 
            size="icon" 
            className="h-8 w-8" 
            onClick={() => onReject(persona, feedback)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-48">
          <div className="space-y-2">
            {feedback.key_insights && (
              <div>
                <h4 className="font-semibold">Key Insights</h4>
                <ul className="list-disc pl-4">
                  {feedback.key_insights.map((insight, idx) => (
                    <li key={idx} className="text-sm">{insight}</li>
                  ))}
                </ul>
              </div>
            )}
            {feedback.improvement_suggestions && (
              <div>
                <h4 className="font-semibold">Suggestions</h4>
                <ul className="list-disc pl-4">
                  {feedback.improvement_suggestions.map((suggestion, idx) => (
                    <li key={idx} className="text-sm">{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

const PRDAnalyzer = () => {
  const [prdText, setPrdText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [feedbackData, setFeedbackData] = useState(null);
  const [orchestratorFeedback, setOrchestratorFeedback] = useState('');
  const [acceptedFeedback, setAcceptedFeedback] = useState([]);
  const [rejectedFeedback, setRejectedFeedback] = useState([]);

  const analyzePRD = async () => {
    setIsAnalyzing(true);
    try {
      // Mock API call - replace with actual backend call
      const mockResponse = {
        product_manager: {
          key_insights: [
            "Market opportunity not clearly defined",
            "Success metrics need quantitative targets"
          ],
          improvement_suggestions: [
            "Add specific market size estimates",
            "Define clear KPI targets"
          ]
        },
        ux_designer: {
          key_insights: [
            "User journey not detailed enough",
            "Missing accessibility considerations"
          ],
          improvement_suggestions: [
            "Include user flow diagrams",
            "Add accessibility requirements"
          ]
        },
        marketing: {
          key_insights: [
            "Value proposition needs refinement",
            "Competitor analysis missing"
          ],
          improvement_suggestions: [
            "Clarify unique selling points",
            "Add competitive landscape analysis"
          ]
        },
        engineer: {
          key_insights: [
            "Technical requirements not specified",
            "Performance criteria unclear"
          ],
          improvement_suggestions: [
            "Define technical stack requirements",
            "Specify performance benchmarks"
          ]
        }
      };
      
      setFeedbackData(mockResponse);
      setOrchestratorFeedback(
        "Based on all persona feedback, the PRD needs stronger market positioning, " +
        "clearer technical specifications, and more detailed user experience flows. " +
        "Priority should be given to defining quantitative success metrics and technical requirements."
      );
    } catch (error) {
      console.error('Error analyzing PRD:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAcceptFeedback = (persona, feedback) => {
    setAcceptedFeedback([...acceptedFeedback, { persona, feedback }]);
    setRejectedFeedback(rejectedFeedback.filter(f => f.persona !== persona));
  };

  const handleRejectFeedback = (persona, feedback) => {
    setRejectedFeedback([...rejectedFeedback, { persona, feedback }]);
    setAcceptedFeedback(acceptedFeedback.filter(f => f.persona !== persona));
  };

  return (
    <div className="flex h-screen">
      {/* Left panel - Input */}
      <div className="w-1/2 p-6 border-r">
        <h2 className="text-2xl font-bold mb-4">PRD Analysis</h2>
        <Textarea
          placeholder="Enter your PRD or product concept here..."
          className="min-h-[400px] mb-4"
          value={prdText}
          onChange={(e) => setPrdText(e.target.value)}
        />
        <Button 
          onClick={analyzePRD} 
          disabled={!prdText || isAnalyzing}
          className="w-full"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            'Improve PRD'
          )}
        </Button>
      </div>

      {/* Right panel - Feedback */}
      <div className="w-1/2 p-6">
        <Tabs defaultValue="personas">
          <TabsList className="mb-4">
            <TabsTrigger value="personas">
              <UserCircle className="mr-2 h-4 w-4" />
              Persona Feedback
            </TabsTrigger>
            <TabsTrigger value="orchestrator">
              <Users className="mr-2 h-4 w-4" />
              Orchestrator Summary
            </TabsTrigger>
          </TabsList>

          <TabsContent value="personas">
            {feedbackData && Object.entries(feedbackData).map(([persona, feedback]) => (
              <PersonaFeedback
                key={persona}
                persona={persona.replace('_', ' ').toUpperCase()}
                feedback={feedback}
                onAccept={handleAcceptFeedback}
                onReject={handleRejectFeedback}
              />
            ))}
          </TabsContent>

          <TabsContent value="orchestrator">
            {orchestratorFeedback && (
              <Card>
                <CardHeader>
                  <CardTitle>Orchestrator Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <Alert>
                    <AlertDescription>
                      {orchestratorFeedback}
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default PRDAnalyzer;
