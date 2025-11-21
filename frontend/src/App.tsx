import React, { useState } from "react";
import {
  Title1,
  Body1,
  Card,
  CardHeader,
  CardPreview,
  Field,
  Input,
  Textarea,
  Button,
  Tag,
  TagGroup,
  Spinner,
} from "@fluentui/react-components";
import { useAppStyles } from "./styles/appStyles";

const App: React.FC = () => {
  const styles = useAppStyles();

  const [subject, setSubject] = useState("");
  const [fromEmail, setFromEmail] = useState("");
  const [fromName, setFromName] = useState("");
  const [recipients, setRecipients] = useState<string[]>([]);
  const [recipientInput, setRecipientInput] = useState("");
  const [prompt, setPrompt] = useState("");
  const [cron, setCron] = useState("*/2 * * * *"); // default: every 2 minutes for testing
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const backendBaseUrl = "http://localhost:8000";

  const handleAddRecipient = () => {
    const trimmed = recipientInput.trim();
    if (!trimmed) return;
    if (recipients.includes(trimmed)) {
      setRecipientInput("");
      return;
    }
    setRecipients((prev) => [...prev, trimmed]);
    setRecipientInput("");
  };

  const handleRemoveRecipient = (email: string) => {
    setRecipients((prev) => prev.filter((r) => r !== email));
  };

  const handleSubmit: React.FormEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault();
    setStatus(null);

    if (!fromEmail || recipients.length === 0 || !prompt) {
      setStatus("Please fill in From Email, at least one recipient, and a prompt.");
      return;
    }

    setLoading(true);
    try {
     

      const payload = {
        from_email: fromEmail,
        from_name: fromName || null,
        subject: subject,
        recipients,
        prompt: prompt,
        cron,
      };

      const res = await fetch(`${backendBaseUrl}/schedule-staggered-email-job`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to schedule email job");
      }

      setStatus(`Job scheduled! Job ID: ${data.job_id}`);
    } catch (err: any) {
      console.error(err);
      setStatus(`Error: ${err.message || "Something went wrong."}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.root}>
      <div className={styles.container}>
        <div className={styles.titleWrapper}>
          <Title1>Rads Automatic Email sender</Title1>
          <Body1 className={styles.subtitle}>
            Configure a prompt, recipients, and schedule to let Rad&apos;s bot
            handle your emails automatically.
          </Body1>
        </div>

        <Card className={styles.card}>
          <CardHeader
            header={<b>Schedule a staggered email job</b>}
            description="Each run sends to the next recipient in the list until all have received an email."
          />
          <CardPreview>
            <form onSubmit={handleSubmit} className={styles.formGrid}>
              <Field label="Email subject (optional)">
                <Input
                  placeholder="e.g. Weekly sales update"
                  value={subject}
                  onChange={(_, data) => setSubject(data.value)}
                />
              </Field>

              <Field label="Email you are sending from">
                <Input
                  type="email"
                  placeholder="yourgmail@gmail.com"
                  value={fromEmail}
                  onChange={(_, data) => setFromEmail(data.value)}
                  required
                />
              </Field>

              <Field label="Your name (shown in the email 'From' field)">
                <Input
                  placeholder="Rad"
                  value={fromName}
                  onChange={(_, data) => setFromName(data.value)}
                />
              </Field>

              <Field label="Recipients">
                <div className={styles.recipientsRow}>
                  <Input
                    type="email"
                    placeholder="Add recipient email"
                    value={recipientInput}
                    onChange={(_, data) => setRecipientInput(data.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleAddRecipient();
                      }
                    }}
                  />
                  <Button type="button" onClick={handleAddRecipient}>
                    Add
                  </Button>
                </div>
                {recipients.length > 0 && (
                  <div className={styles.tagGroupWrapper}>
                    <TagGroup>
                      {recipients.map((email) => (
                        <Tag
                          key={email}
                          dismissible
                          onDismiss={() => handleRemoveRecipient(email)}
                        >
                          {email}
                        </Tag>
                      ))}
                    </TagGroup>
                  </div>
                )}
              </Field>

              <Field label="Prompt for the email body">
                <Textarea
                  placeholder="Explain what the email should say and how it should sound."
                  value={prompt}
                  onChange={(_, data) => setPrompt(data.value)}
                  rows={5}
                  required
                />
              </Field>

              <Field label="Cron schedule expression">
                <Input
                  placeholder="*/2 * * * *  (every 2 minutes)"
                  value={cron}
                  onChange={(_, data) => setCron(data.value)}
                />
                <Body1>
                  Example: <code>*/2 * * * *</code> = every 2 minutes.{" "}
                  <code>0 9 * * *</code> = every day at 9:00.
                </Body1>
              </Field>

              <div className={styles.footer}>
                <Button appearance="primary" type="submit" disabled={loading}>
                  {loading ? (
                    <>
                      <Spinner size="tiny" />
                      &nbsp;Scheduling...
                    </>
                  ) : (
                    "Schedule job"
                  )}
                </Button>
                <Body1 className={styles.statusText}>
                  {status && status}
                </Body1>
              </div>
            </form>
          </CardPreview>
        </Card>
      </div>
    </div>
  );
};

export default App;
