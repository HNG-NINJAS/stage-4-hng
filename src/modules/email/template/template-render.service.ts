import { Injectable } from "@nestjs/common";
interface Template{
    subject:string
    body:string
}
@Injectable()
export class TemplateRendererService{
    render(template:Template,variables:Record<string,string>){
        let subject= template.subject
        let html_body = template.body

        for (const [key, value] of Object.entries(variables)) {
      const placeholder = new RegExp(`{{${key}}}`, 'g');
      subject = subject.replace(placeholder, value);
      html_body = html_body.replace(placeholder, value);
    }
    return {subject,html_body}
    }
   
}